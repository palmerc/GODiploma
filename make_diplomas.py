#!/usr/bin/env python3

import argparse
import csv
import svgutils
from lxml import etree
from enum import Enum
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics


TOP_TEXT_FORMAT = 'Diplomet tildeles {} i Gamle Oslo String Orchestra'
BOTTOM_TEXT = 'for vel gjennomført program våren 2021'


class Orchestra(Enum):
    NONE = 0
    ASPIRANT = 1
    MAIN = 2


class Member:
    def __init__(self, row):
        self.row = row

    def name(self):
        member_name = self.row['Name']
        return member_name.strip().replace('\\s+', '\\s')

    def type(self):
        orchestra = self.row['Type']
        if orchestra == 'ASPIRANT':
            return Orchestra.ASPIRANT
        elif orchestra == 'MAIN':
            return Orchestra.MAIN
        else:
            return Orchestra.NONE

    def orchestra(self):
        orchestra = None
        if self.type() == Orchestra.ASPIRANT:
            orchestra = 'Aspirant'
        elif self.type() == Orchestra.MAIN:
            orchestra = 'Orkestermedlem'

        return orchestra


def members_from_csv(csv_path):
    students = []
    with open(csv_path) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';', quotechar='"')
        for row in reader:
            students.append(Member(row))
    return students


def insert_member_name(text_el, member):
    member_name = member.name()
    parts = member_name.split(' ')
    text_chunks = [parts[i:i + 2] for i in range(0, len(parts), 2)]

    for child in text_el.getchildren():
        text_el.remove(child)

    if len(text_chunks) == 1:
        line = etree.Element(svgutils.transform.SVG + "tspan", {"x": "50%", "y": "290"})
        line.text = ' '.join(text_chunks[0])
        text_el.append(line)

    if len(text_chunks) == 2:
        line1 = etree.Element(svgutils.transform.SVG + "tspan", {"x": "50%", "y": "250"})
        line1.text = ' '.join(text_chunks[0])
        line2 = etree.Element(svgutils.transform.SVG + "tspan", {"x": "50%", "y": "319"})
        line2.text = ' '.join(text_chunks[1])

        text_el.append(line1)
        text_el.append(line2)


def main():
    parser = argparse.ArgumentParser(description='Print diplomas')
    parser.add_argument('-m', '--members', dest='members',
                        help='set the member csv to use', default="./members.csv")
    parser.add_argument('-t', '--template', dest='template',
                        help='a template of the diploma', default='./GO_Diploma.svg')
    args = parser.parse_args()

    members = members_from_csv(args.members)
    diploma = svgutils.transform.fromfile(args.template)
    for member in members:
        print('Diploma for {} {}'.format(member.orchestra(), member.name()))
        top_text_el = diploma.find_id('TOP_TEXT').root
        top_text_el.text = TOP_TEXT_FORMAT.format(member.orchestra())

        insert_member_name(diploma.find_id('MEMBER_NAME').root, member)

        bottom_text_el = diploma.find_id('BOTTOM_TEXT').root
        bottom_text_el.text = BOTTOM_TEXT

        basename = member.name().replace(' ', '_')
        orchestra = member.orchestra()
        filename_base = './member-{}-{}'.format(basename, orchestra.lower())
        svg_filename = filename_base + '.svg'
        diploma.save(svg_filename)
        report_lab_graphic = svg2rlg(svg_filename)
        pdfmetrics.registerFont(TTFont('Coustard', './fonts/Coustard-Regular.ttf'))
        pdfmetrics.registerFont(TTFont('Glacial Indifference', './fonts/GlacialIndifference-Regular.ttf'))
        pdf_filename = filename_base + '.pdf'
        renderPDF.drawToFile(report_lab_graphic, pdf_filename)


if __name__ == '__main__':
    main()
