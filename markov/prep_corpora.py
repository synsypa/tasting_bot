import csv
import os
import re
from logzero import logger

DATA_PATH = '../corpora/'

START1_TOK = '<START1>'
START2_TOK = '<START2>'
END_TOK = '<END>'


class CorpusCleaner():

    def __init__(self, bigram_start=True):
        self.start1 = START1_TOK
        # This is some hackiness to avoid weird spaces
        self.start2 = f" {START2_TOK}" if bigram_start else ""
        self.end = END_TOK

    def _process_line(self, line):
        cleaned = re.sub("\s+", " ", line.strip().replace("'", ""))
        return f"{self.start1}{self.start2} {cleaned} {self.end}"

    def clean_lines(self, lines):
        return [self._process_line(line) for line in lines]


class BookCleaner(CorpusCleaner):

    def __init__(self, filename, bigram_start=True):
        super().__init__(bigram_start)

        self.filename = filename

    def _open_file(self):
        with open(self.filename, 'r', encoding='utf-8-sig') as f:
            all_book = f.read()
        return all_book

    def clean_lines(self):
        text = self._open_file()
        paragraphs = [
            self._process_line(l)
            for l in re.split('\n\n+', text)
        ]
        return paragraphs


class BibleCleaner(BookCleaner):

    def __init__(self, filename, bigram_start=True):
        super().__init__(filename, bigram_start)

    def clean_lines(self):
        text = self._open_file()
        verses = [
            self._process_line(v)
            for v in re.split("\d\d*:\d\d*", text)
        ]
        return verses


class AnalectCleaner(BookCleaner):

    def __init__(self, filename, bigram_start=True):
        super().__init__(filename, bigram_start)

    def clean_lines(self):
        text = self._open_file()
        books = re.split('BOOK.*\n\n', text)[1:]
        chapters = []
        for b in books:
            chapters.extend(re.split('CHAP. [XIV]+.|CHAPTER.[XIV]+.', b.strip()))
        lines = [
            self._process_line(re.sub("\d\d*.", "", v))
            for v in chapters
        ]
        return lines


class WineCleaner(CorpusCleaner):

    def __init__(self, filename, bigram_start=True):
        super().__init__(bigram_start)

        self.filename = filename

    def _open_csv(self):
        with open(self.filename, 'r') as f:
            notes = csv.reader(f, delimiter='\036')
            return [n for n in notes]

    def clean_lines(self):
        scraped = self._open_csv()
        notes = [self._process_line(f"{n[2]}: {n[6]}") for n in scraped]
        names = [
            self._process_line(f"{n[0]}: {n[2]}") if n[2] == 'NV'
            else self._process_line(n[0])
            for n in scraped
        ]
    
        return notes, names

def clean_all(corpora_path):
    merged_notes = []
    merged_names = []
    for filebase in os.listdir(corpora_path):
        file = os.path.join(corpora_path, filebase)
        logger.info(f"Processing {file}...")
        if os.path.splitext(file)[1] == '.csv':
            wine_cleaner = WineCleaner(file)
            notes, names = wine_cleaner.clean_lines()
            merged_notes.extend(notes)
            merged_names.extend(names)
        # elif os.path.basename(file) == 'bible.txt':
        #     b_cleaner = BibleCleaner(file)
        #     merged_notes.extend(b_cleaner.clean_lines())
        elif os.path.basename(file) == 'artofwar.txt':
            w_cleaner = BookCleaner(file)
            merged_notes.extend(w_cleaner.clean_lines())
        elif os.path.basename(file) == 'redchamber.txt':
            r_cleaner = BookCleaner(file)
            merged_notes.extend(r_cleaner.clean_lines())
        elif os.path.basename(file) == 'analects.txt':
            a_cleaner = AnalectCleaner(file)
            merged_notes.extend(a_cleaner.clean_lines())
        else:
            logger.error(f"Don't know how to process {file}")
            continue

    return merged_notes, merged_names
            

if __name__ == "__main__":
    notes, names = clean_all(DATA_PATH)

    logger.info("Saving merged notes...")
    with open("notes_merged.csv", "w") as f:
        for n in notes:
            f.write(f"{n}\n")

    logger.info("Saving merged names...")
    with open("names_merged.csv", "w") as f:
        for n in names:
            f.write(f"{n}\n")

