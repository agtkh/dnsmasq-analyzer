#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author: K.Agata
Date: 2024/09/06

"""

import time
import os
import sys
import stat
import publicsuffix2
import pymysql
import requests
from bs4 import BeautifulSoup
import threading


def main():
    # データベース接続情報
    host = os.getenv("DNSMASQ_ANLZR_DB_HOST")
    user = os.getenv("DNSMASQ_ANLZR_DB_USER")
    password = os.getenv("DNSMASQ_ANLZR_DB_PASSWORD")
    database = os.getenv("DNSMASQ_ANLZR_DB_DATABASE")

    # ログファイルのパス
    log_filename = os.getenv("DNSMASQ_ANLZR_LOG_FILENAME")
    print(f"{host=}", file=sys.stderr)
    print(f"{user=}", file=sys.stderr)
    print(f"{password=}", file=sys.stderr)
    print(f"{database=}", file=sys.stderr)
    print(f"{log_filename=}", file=sys.stderr)

    db = Database(host, user, password, database)

    analyzer = DnsmasqAnalyzer(log_filename, db)
    analyzer.start(1000)


class Database:
    def __init__(self, host, user, password, database):
        self.conn = pymysql.connect(
            host=host, user=user, password=password, database=database
        )

    def increment_count(self, date_str, domain_name, source):
        sql = """
            INSERT INTO queries (domain_name, source, count, last)
            VALUES (%s, %s, %s, NOW())
            ON DUPLICATE KEY UPDATE count = count + 1, last = NOW()
        """
        with self.conn.cursor() as cursor:
            cursor.execute(sql, (domain_name, source, 1))
        self.conn.commit()

    def check_title_exists(self, url):
        with self.conn.cursor() as cursor:
            sql = "SELECT COUNT(*) FROM titles WHERE url=%s"
            cursor.execute(sql, (url,))
            res = cursor.fetchone()
        if res is None:
            print("warning", file=sys.stderr)
        return res is None or  res[0]

    def insert_title(self, url):
        title = get_website_title(url)
        
        with self.conn.cursor() as cursor:
            sql = "INSERT IGNORE INTO titles (url, title) VALUES (%s, %s)"
            cursor.execute(sql, (url, title))
        self.conn.commit()

    def __del__(self):
        if hasattr(self, 'conn'):  self.conn.close()


def get_website_title(url):
    if not url.startswith("http"):
        url = "https://" + url
    try:
        response = requests.get(url, timeout=3.0)
        response.raise_for_status()  # エラーが発生した場合、例外を発生させる
        if response.status_code != 200:
            return "-"

        soup = BeautifulSoup(response.content, "html.parser")
        title = soup.find("title")

        if title:
            return (
                title.text.strip()
            )  # タイトルが存在すれば、テキストを返す（空白を除去）
        else:
            return "-"
    except (requests.exceptions.RequestException, requests.exceptions.Timeout) as e:
        return "-"


class DnsmasqAnalyzer:
    def __init__(self, filename, db):
        self.file = open(filename, "r")
        self.db: Database = db
        self.psl_file = publicsuffix2.fetch()

        # ファイル末尾へ移動
        st_results = os.stat(filename)
        st_size = st_results[stat.ST_SIZE]
        self.file.seek(st_size)

    def start(self, usec):
        assert not self.file.closed
        msec = usec / 1000
        while True:
            fpos = self.file.tell()
            line = self.file.readline()
            if not line:
                time.sleep(msec)
                self.file.seek(fpos)
            else:
                self.analyze_line(line)

    def analyze_line(self, line):
        splitted = line.strip().split()

        # filter
        if len(splitted) != 8 or splitted[4] != "query[A]":
            #   not splitted[4].startswith('query'):
            return
        date_str = " ".join(splitted[:3])
        domain_name = publicsuffix2.get_sld(splitted[5], psl_file=self.psl_file)
        sender_ip = splitted[7]
        self.db.increment_count(date_str, domain_name, sender_ip)

        if not self.db.check_title_exists(domain_name):
            threading.Thread(target=self.db.insert_title, args=(domain_name,)).start()

    def __del__(self):
        assert not self.file.close()
        self.file.close()


if __name__ == "__main__":
    main()
