#!/usr/bin/python
# -*- coding: UTF-8 -*-

import requests
import json
from datetime import datetime
import codecs
import os
import re
import sys
import argparse

URL_MainMapData = "http://stat.gibdd.ru/map/getMainMapData"
URL_DTPCardData = "http://stat.gibdd.ru/map/getDTPCardData"
log_filename = "parselog.log"


def get_latest_date():
    year = datetime.now().year
    if datetime.now().month > 2:
        last_month = datetime.now().month - 1
    else:  # январь. придется брать данные за декабрь предыдущего года
        year -= 1
        last_month = 12
    return {"month": last_month, "year": year}


# шаг 1) получаем ОКАТО-коды всех регионов РФ (877 - код РФ)
# по умолчанию берем самые свежие данные, за месяц перед текущим (ГИБДД выгружает данные с отставанием на 1 месяц)
def get_rus_fed_data():
    latest_m_y = get_latest_date()
    rf_dict = {"maptype": 1,
               "region": "877",
               "date": "[\"MONTHS:{0}.{1}\"]".format(latest_m_y["month"],
                                                     latest_m_y["year"]),
               "pok": "1"}
    r = requests.post(URL_MainMapData, json=rf_dict)

    if r.status_code != 200:
        log_text = "Не удалось получить данные по регионам РФ"
        print(log_text)
        write_log(log_text)
        return None
    else:
        log_text = "Получены данные по регионам РФ"
        print(log_text)
        write_log(log_text)
        return r.content


# пары код ОКАТО + название региона
def get_regions_info():
    content = get_rus_fed_data()
    if content is None:
        return None
    else:
        regions = []
        d = (json.loads(content))
        regions_dict = json.loads(json.loads(d["metabase"])[0]["maps"])
        for rd in regions_dict:
            regions.append({"id": rd["id"],
                            "name": rd["name"]})
        return regions


# шаг 2) получаем ОКАТО-коды муниципальных образований для всех регионов
# по умолчанию берем самые свежие данные, за месяц перед текущим
def get_region_data(region_id, region_name):
    latest_m_y = get_latest_date()
    region_dict = {"maptype": 1, "date": "[\"MONTHS:{0}.{1}\"]".format(latest_m_y["month"],
                                                                       latest_m_y["year"]), "pok": "1",
                   "region": region_id}
    r = requests.post(URL_MainMapData, json=region_dict)

    if r.status_code != 200:
        log_text = "Не удалось получить статистику по региону {0} {1}".format(region_id, region_name)
        print(log_text)
        write_log(log_text)
        return None
    else:
        log_text = "Получена статистика по региону {0} {1}".format(region_id, region_name)
        print(log_text)
        write_log(log_text)
        return r.content


# пары код ОКАТО + название муниципального образования для всех регионов
def get_districts_info(region_id, region_name):
    content = get_region_data(region_id, region_name)
    if content is None:
        return None
    else:
        d = (json.loads(content))
        district_dict = json.loads(json.loads(d["metabase"])[0]["maps"])
        districts = []
        for dd in district_dict:
            districts.append({"id": dd["id"], "name": dd["name"]})
        return json.dumps(districts).encode('utf8').decode('unicode-escape')


# сохраняем справочник ОКАТО-кодов и названий регионов и муниципалитетов
def save_code_dictionary(filename):
    region_codes = get_regions_info()
    for region in region_codes:
        region["districts"] = get_districts_info(region["id"], region["name"])

    with codecs.open(filename, "w", encoding="utf-8") as f:
        json.dump(region_codes, f, ensure_ascii=False)


# шаг 3) получаем карточки ДТП по заданному региону за указанный период
# st и en - номер первой и последней карточки, т.к. на ресурсе - постраничный перебор данных
def get_dtp_data(region_id, region_name, district_id, district_name, months, year):
    cards_dict = {"data": {"date": ["MONTHS:1.2018"],
                           "ParReg": "71100",
                           "order": {"type": "1",
                                     "fieldName": "dat"},
                           "reg": "71118",
                           "ind": "1",
                           "st": "1",
                           "en": "16"}}
    cards_dict["data"]["ParReg"] = region_id
    cards_dict["data"]["reg"] = district_id
    months_list = []
    json_data = None
    for month in months:
        months_list.append("MONTHS:" + str(month) + "." + str(year))
    cards_dict["data"]["date"] = months_list
    # постраничный перебор карточек
    start = 1
    increment = 50  # можно 100, не стоит 1000, т.к. можно словить таймаут запроса

    while True:
        cards_dict["data"]["st"] = str(start)
        cards_dict["data"]["en"] = str(start + increment - 1)
        # генерируем компактную запись json, без пробелов. иначе сайт не воспринимает данные
        cards_dict_json = {"data": json.dumps(cards_dict["data"],
                                              separators=(",", ":")).encode("utf8").decode("unicode-escape")}

        r = requests.post(URL_DTPCardData, json=cards_dict_json)
        if r.status_code == 200:
            cards = json.loads(json.loads(r.content)["data"])["tab"]
            if len(cards) > 0:
                if json_data is None:
                    json_data = cards
                else:
                    json_data = json_data + cards
            if len(cards) == increment:
                start += increment
            else:
                break
        else:
            if "Unexpected character (',' (code 44))" in r.text:  # карточки закончились
                break
            # if "No content to map due to end-of-input" in r.text: # или ошибка JS - для этого района нет данных
            else:
                log_text = "Отсутствуют данные для {0} ({1}) за {2}-{3}.{4}".format(region_name,
                                                                                    district_name,
                                                                                    months[0],
                                                                                    months[len(months) - 1],
                                                                                    year)
                print(log_text)
                write_log(log_text)
                break

    return json_data


# шаг 4) сохраняем статистику ДТП. один файл = один регион за один год
# пример наименования файла: "98 Республика Саха (Якутия) 1-4.2018.json"
# region_id = '0' - данные по всем регионам. иначе region_id = ОКАТО-номер региона
# важно! движок отдает все загруженные на сайт карточки, поэтому их может оказаться больше, чем в интерфейсе пользователя
# реализована догрузка: парсер не будет повторно качать уже загруженные данные
def get_dtp_info(data_root, year, months, regions, region_id="0"):
    data_dir = os.path.join(data_root, year)

    regions_downloaded = []
    if os.path.exists(data_dir):
        files = [x for x in os.listdir(data_dir) if x.endswith(".json")]
        for file in files:
            result = re.match("([0-9]+)([^0-9]+)(.*)", file)
            regions_downloaded.append(result.group(2).strip())

    for region in regions:
        # была запрошена статистика по одному из регионов, а не по РФ
        if region_id != "0" and region["id"] != region_id:
            continue
        json_file_name = f"{region_id} {region['name']} {months[0]}-{months[-1]}.{year}.json"
        # if region["name"] in regions_downloaded:
        if os.path.exists(os.path.join(data_root, year, json_file_name)):
            log_text = "Статистика по региону {} уже загружена".format(region["name"])
            print(log_text)
            write_log(log_text)
            continue

        dtp_dict = {"data": {}}
        dtp_dict["data"]["year"] = str(year)
        dtp_dict["data"]["region_code"] = region["id"]
        dtp_dict["data"]["region_name"] = region["name"]
        dtp_dict["data"]["month_first"] = months[0]
        dtp_dict["data"]["month_last"] = months[-1]

        dtp_dict["data"]["cards"] = []

        # муниципальные образования в регионе
        districts = json.loads(region["districts"])
        for district in districts:
            # получение карточек ДТП
            log_text = "Обрабатываются данные для {0} ({1}) за {2}-{3}.{4}".format(region["name"],
                                                                                   district["name"],
                                                                                   months[0],
                                                                                   months[-1],
                                                                                   year)
            print(log_text)
            write_log(log_text)
            cards = get_dtp_data(region["id"], region["name"], district["id"], district["name"], months, year)
            if cards is None:
                continue

            log_text = "{0} ДТП для {1} ({2}) за {3}-{4}.{5}".format(len(cards),
                                                                     region["name"],
                                                                     district["name"],
                                                                     months[0],
                                                                     months[len(months) - 1],
                                                                     year)
            print(log_text)
            write_log(log_text)
            dtp_dict["data"]["cards"] += cards

        dtp_dict_json = {"data": json.dumps(dtp_dict["data"]).encode("utf8").decode("unicode-escape")}
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        filename = os.path.join(data_dir, "{} {} {}-{}.{}.json".format(region["id"],
                                                                       region["name"],
                                                                       months[0],
                                                                       months[len(months) - 1],
                                                                       year))
        with codecs.open(filename, "w", encoding="utf-8") as f:
            json.dump(dtp_dict_json, f, ensure_ascii=False, separators=(',', ':'))
            log_text = "Сохранены данные для {} за {}-{}.{}".format(region["name"],
                                                                    months[0],
                                                                    months[len(months) - 1],
                                                                    year)
            print(log_text)
            write_log(log_text)

        # если запрошены данные только по одному региону
        if region["id"] == region_id:
            break


def read_dtp_data(filename):
    with codecs.open(filename, "r", encoding="utf-8") as f:
        json_content = json.loads(json.loads(json.loads(json.dumps(f.read())))["data"])
    dtp_data = json_content["cards"]

    pog = 0
    ran = 0
    for dtp_data1 in dtp_data:
        pog += int(dtp_data1["POG"])
        ran += int(dtp_data1["RAN"])

    result = {
        "dtp_count": str(len(dtp_data)),
        "pog": str(pog),
        "ran": str(ran),
        "proc": f"{(ran / pog):.2f}%",
        "dtp_data": {}
        }

    for index, dtp_data1 in enumerate(dtp_data):
        result["dtp_data"][f"dtp_{index:05}"] = {}
        result["dtp_data"][f"dtp_{index:05}"]["index"] = index
        date = f"{dtp_data1['date'][6:]}.{dtp_data1['date'][3:5]}.{dtp_data1['date'][0:2]}"
        result["dtp_data"][f"dtp_{index:05}"]["date"] = date
        result["dtp_data"][f"dtp_{index:05}"]["District"] = dtp_data1["District"]
        result["dtp_data"][f"dtp_{index:05}"]["DTP_V"] = dtp_data1["DTP_V"]
        result["dtp_data"][f"dtp_{index:05}"]["POG"] = dtp_data1["POG"]
        result["dtp_data"][f"dtp_{index:05}"]["RAN"] = dtp_data1["RAN"]
        result["dtp_data"][f"dtp_{index:05}"]["K_TS"] = dtp_data1["K_TS"]
        result["dtp_data"][f"dtp_{index:05}"]["K_UCH"] = dtp_data1["K_UCH"]
    return result


def create_parser():
    parser = argparse.ArgumentParser(
        description="gibdd_stat_parser.py [--year] [--month] [--regcode] [--dir] [--updatecodes] [--help]")
    parser.add_argument("--year",
                        type=str,
                        help="год, за который скачивается статистика. пример: --year 2017")
    parser.add_argument("--month",
                        type=str,
                        help="месяц, за который скачивается статистика. пример: --month 1. не указан - скачиваются все")
    parser.add_argument("--regcode",
                        default="0",
                        type=str,
                        help="ОКАТО-код региона (см. в regions.json). \
                              пример для Новосибирской области: --regcode 50. не указан - скачиваются все")
    parser.add_argument("--dir",
                        default="dtpdata",
                        type=str,
                        help="каталог для сохранения карточек ДТП. по умолчанию dtpdata")
    parser.add_argument("--updatecodes",
                        default="n",
                        help="обновить справочник регионов. пример: --updatecodes y")
    return parser


def create_log():
    with open(log_filename, "w") as f:
        pass


def write_log(text):
    timestamp = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
    with open(log_filename, "a") as f:
        f.write("{} {}\n".format(timestamp, text))


def main():
    parser = create_parser()
    namespace = parser.parse_args(sys.argv[1:])

    data_root = namespace.dir
    if not os.path.exists(data_root):
        os.makedirs(data_root)

    if not os.path.exists(log_filename):
        create_log()

    if len(namespace.updatecodes) > 0:
        if namespace.updatecodes == "y":
            log_text = "Обновление справочника кодов регионов..."
            print(log_text)
            write_log(log_text)
            save_code_dictionary("regions.json")
            log_text = "Обновление справочника завершено"
            print(log_text)
            write_log(log_text)
        elif namespace.updatecodes == "n":
            log_text = "Обновление справочника отменено"
            print(log_text)
            write_log(log_text)

    # получаем год (если параметр опущен - текущий год)
    if namespace.year is not None:
        year = namespace.year
    else:
        year = datetime.now().year

    # получаем месяц (если параметр опущен - все прошедшие месяцы года)
    if namespace.month is not None:
        months = [int(namespace.month)]
    else:
        if year == str(datetime.now().year):
            months = list(range(1, datetime.now().month, 1))
        else:
            months = list(range(1, 13, 1))

    # загружаем данные из справочника ОКАТО-кодов регионов и муниципалитетов
    filename = "regions.json"
    with codecs.open(filename, "r", "utf-8") as f:
        regions = json.loads(json.loads(json.dumps(f.read())))

    get_dtp_info(data_root,
                 year,
                 months,
                 regions,
                 region_id=namespace.regcode)


# для вызова скрипта из командной строки
if __name__ == "__main__":
    log_text = "Парсер сайта статистики ГИБДД"
    print(log_text)
    main()
