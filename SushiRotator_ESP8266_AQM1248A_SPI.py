#
# Sushi rotator for ESP8266 & AQM1248A(SPI) with MicroPython
# Copyright (c) 2016 nobukuma
#
# This code is licensed under Apache v2.0 License
# (http://www.apache.org/licenses/LICENSE-2.0)
#

from machine import SPI
from machine import Pin
import time

# 寿司ビットマップデータ
from data import icon

# スクロールのオフセット
SCROLLOFFSET = 3

# 初期位置
INITIALOFFSET = -47

# SPI設定(Hardware SPI)
RSnum = 5
CSnum = 4

RS = Pin(RSnum, Pin.OUT)
CS = Pin(CSnum, Pin.OUT)

spi = SPI(1, baudrate=80000000, polarity=0, phase=0)
spi.init(baudrate=80000000)

# LCD制御
# コマンド送信
def lcdCmd(cmd):
    RS.low()
    CS.low()
    value = cmd.to_bytes(1, 'big')
    spi.write(value)
    RS.high()
    CS.high()

# データ送信
def lcdData(data):
    RS.high()
    CS.low()
    value = data.to_bytes(1, 'big')
    spi.write(value)
    RS.high()
    CS.high()

# ページ選択
def selectPage(page):
    lcdCmd(0xB0 | (page & 0x0F))

# カラム選択
def selectColumn(col):
    lcdCmd(0x10 | ((col >> 4) & 0x0F))
    lcdCmd(0x00 | (col & 0x0F))

# ディレイ
def delay(durationInMSec):
    time.sleep_ms(durationInMSec)

# 初期化処理
def initLCD():
    lcdCmd(0xAE)
    lcdCmd(0xA0)
    lcdCmd(0xC8)
    lcdCmd(0xA3)

    # 内部レギュレータON
    lcdCmd(0x2C)           
    delay(2)
    lcdCmd(0x2E)
    delay(2)
    lcdCmd(0x2F)

    # コントラスト設定
    lcdCmd(0x23)
    lcdCmd(0x81)
    lcdCmd(0x1C)

    # 表示設定
    lcdCmd(0xA4)
    lcdCmd(0x40)
    lcdCmd(0xA6)
    lcdCmd(0xAF)

# 描画処理
# x-scrolloffset .. x+47までをクリア＆描画する
def drawSushi(x, scrolloffset):
    for page in range(0, 6):
        selectPage(page)
        
        # x - scrolloffset .. x - 1まではクリア
        for col in range(x - scrolloffset, x):
            if col >= 0 and col < 128:
                selectColumn(col)
                lcdData(0)

        # x .. x+47は描画
        for col in range(x, x + 48):
            selectColumn(col)
            if col >= 0 and col < 128:
                value = 0
                for offset in range(0, 8):
                    row =  page * 8 + offset
                    pixelValue = icon[row][col-x]
                    value = value | pixelValue << offset
                lcdData(value)

# 画面の全消去
def clearAll():
    for page in range(0, 6):
        selectPage(page)
        selectColumn(0)
        for col in range(0, 128):
            lcdData(0)

# メイン処理
def main():
    initLCD()
    clearAll()
    x = INITIALOFFSET
    while True:
        drawSushi(x, SCROLLOFFSET)
        x = x + SCROLLOFFSET
        x = x if x < 128 else INITIALOFFSET

main()
