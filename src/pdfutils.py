################################### PDF Operations Module #####################################
#
# Contains functions for handling PDF files, including parsing and extracting text/images.
#
# #############################################################################################
import pymupdf
from datetime import datetime
import os
from pathlib import Path


class PdfUtils:
    """PDF Utilities for handling PDF files."""

    # minimum fraction of the word area that must be intersected to consider it contained
    _threshold_intersection = 0.5

    def __init__(self, document=None):
        """Initializes the PdfUtils object. Pass `document` to immediately parse annotations."""
        self.document = document
        if document is not None:
            # keep legacy parsed annotations available
            self.annotations = self._parse_annotations(document)

    @staticmethod
    def open_pdf(path):
        """Opens a PDF file.

        Args:
            path (str): path to the PDF file.

        Returns:
            pymupdf.Document: opened PDF document.
        """
        document = pymupdf.open(path)
        return document

    @staticmethod
    def check_annotations(document):
        """Checks if the PDF document contains annotations.

        Args:
            document (pymupdf.Document): PDF document to check.

        Returns:
            bool: True if annotations are present, False otherwise.
        """
        for page in document:
            if page.annots():
                return True
        return False

    @staticmethod
    def get_wordlist(page):
        """Gets the list of words on a PDF page.

        Args:
            page (pymupdf.Page): PDF page to extract words from.

        Returns:
            list: list of words on the page.
        """
        words_on_page = page.get_text("words")  # list of words on the page
        words_on_page.sort(key=lambda w: (w[1], w[0]))  # sort by y1, x0
        return words_on_page

    #  Checks for intersections
    @staticmethod
    def _check_contain(r_word, points):
        """Checks if `r_word` is contained in the rectangular area.

        The area of the intersection should be large enough compared to the
        area of the given word.

        Args:
            r_word (pymupdf.Rect): rectangular area of a single word.
            points (list): list of points in the rectangular area of the
                given part of a highlight.

        Returns:
            bool: whether `r_word` is contained in the rectangular area.
        """
        # `r` is mutable, so everytime a new `r` should be initiated.
        r = pymupdf.Quad(points).rect
        r.intersect(r_word)

        if r.width * r.height >= (r_word.width * r_word.height) * PdfUtils._threshold_intersection:
            contain = True
        else:
            contain = False
        return contain

    # extract words under the annotations
    @staticmethod
    def _extract_annot(annot, words_on_page):
        """Extracts words in a given highlight.

        Args:
            annot (pymupdf.Annot): [description]
            words_on_page (list): [description]

        Returns:
            str: words in the entire highlight.
        """
        quad_points = annot.vertices
        quad_count = int(len(quad_points) / 4)
        sentences = ["" for i in range(quad_count)]
        for i in range(quad_count):
            points = quad_points[i * 4 : i * 4 + 4]
            words = [
                w
                for w in words_on_page
                if PdfUtils._check_contain(pymupdf.Rect(w[:4]), points)
            ]
            sentences[i] = " ".join(w[4] for w in words)
        sentence = " ".join(sentences)

        return sentence

    # sort annotations
    @staticmethod
    def _sort_annots(page):
        s_annots = [a for a in page.annots()]
        s_annots.sort(key=lambda a: (a.rect.bl.y, a.rect.bl.x))
        return s_annots

    @staticmethod
    def _parse_pdf_date(date_string):
        """
        Parses a PDF date string (e.g., "D:20231120183000+05'30'") into a datetime object.
        """
        if not date_string or not date_string.startswith("D:"):
            return None
        try:
            # Extract the core date-time part, ignoring timezone for simplicity for now.
            # Format is YYYYMMDDHHMMSS
            dt_part = date_string[2:16]
            return datetime.strptime(dt_part, "%Y%m%d%H%M%S")
        except (ValueError, IndexError):
            return None

    def _parse_annotations(self, document):
        """Parses all annotations from the document."""
        parsed_annotations = []
        for page_num in range(len(document)):
            page = document[page_num]
            words_on_page = self.get_wordlist(page)
            if page.annots():
                sorted_annots = self._sort_annots(page)
                for annot in sorted_annots:
                    # Highlight (8), Square (4), Circle (5)
                    annot_type_id = annot.type[0]
                    
                    if annot_type_id == 8:  # Highlight
                        highlight_text = self._extract_annot(annot, words_on_page)
                        user_comment = annot.info.get("content", "")
                        mod_date = self._parse_pdf_date(annot.info.get("modDate"))
                        
                        parsed_annotations.append(
                            {
                                "page": page_num + 1,
                                "type": "Highlight",
                                "highlight_text": highlight_text,
                                "comment": user_comment,
                                "info": annot.info,
                                "modDate": mod_date,
                                "colors": annot.colors,
                                "rect": tuple(annot.rect),
                            }
                        )
                    
                    elif annot_type_id in [4, 5]:  # Square or Circle -> Image Capture
                        user_comment = annot.info.get("content", "")
                        mod_date = self._parse_pdf_date(annot.info.get("modDate"))
                        
                        parsed_annotations.append(
                            {
                                "page": page_num + 1,
                                "type": "Image",
                                "highlight_text": "",
                                "comment": user_comment,
                                "info": annot.info,
                                "modDate": mod_date,
                                "colors": annot.colors,
                                "rect": tuple(annot.rect),
                                "shape_type": "Square" if annot_type_id == 4 else "Circle",
                            }
                        )
        return parsed_annotations

    @staticmethod
    def get_metrics(document, annotations=None):
        """
        Calculates and returns metrics about the PDF and its annotations.

        Args:
            document: pymupdf.Document or an object providing metadata.
            annotations (list, optional): parsed annotations; if None the method
                will try to read `annotations` attribute from `document`.

        Returns:
            dict: A dictionary containing various metrics.
        """
        # If caller didn't provide parsed annotations, prefer document.annotations if available,
        # else collect raw Annot objects from the document.
        annotated_pages = set()
        if annotations is None:
            annotations = getattr(document, "annotations", None) or []
            if not annotations:
                annotations = []
                for page in document:
                    annots = page.annots()
                    if annots:
                        for a in annots:
                            annotations.append(a)
                        annotated_pages.add(page.number + 1)
        else:
            # If annotations provided, collect page numbers from dicts or objects
            for annot in annotations:
                if isinstance(annot, dict):
                    p = annot.get("page")
                    if p:
                        annotated_pages.add(p)
                else:
                    try:
                        # MuPDF Annot objects: get_page() -> Page
                        annotated_pages.add(annot.get_page().number + 1)
                    except Exception:
                        # fallback: try 'page' attribute
                        p = getattr(annot, "page", None)
                        if isinstance(p, int):
                            annotated_pages.add(p)

        total_pages = len(document)
        total_annotations = len(annotations)

        def _maybe_parse_date(ds):
            # ds can be datetime, string like "D:YYYYMMDDHHMMSS", or None
            if isinstance(ds, datetime):
                return ds
            if not ds:
                return None
            if isinstance(ds, str):
                parsed = PdfUtils._parse_pdf_date(ds)
                return parsed or ds
            return None

        annotation_times = []
        for annot in annotations:
            if isinstance(annot, dict):
                raw = annot.get("modDate") or (annot.get("info") or {}).get("modDate")
            else:
                raw = getattr(annot, "info", {}).get("modDate")
            parsed = _maybe_parse_date(raw)
            if parsed:
                annotation_times.append(parsed)

        # prepare user-facing labeled metrics and return them using the requested keys
        metadata = getattr(document, "metadata", {}) or {}
        title = metadata.get("title") or metadata.get("Title") or None

        first_annotated_page = min(annotated_pages) if annotated_pages else None
        last_annotated_page = max(annotated_pages) if annotated_pages else None

        first_annot_time = min(annotation_times) if annotation_times else None
        last_annot_time = max(annotation_times) if annotation_times else None

        return {
            "Title": title,
            "Pages": total_pages,
            "Annotated pages": len(annotated_pages),
            "Total annotations": total_annotations,
            "First annotated on page": first_annotated_page,
            "Last annotated on page": last_annotated_page,
            "First annotated at": first_annot_time,
            "Last annotated at": last_annot_time,
        }

    @staticmethod
    def get_image_folder(notes_folder, pdf_basename):
        """Creates and returns the path to the image folder for a given PDF."""
        image_folder = Path(notes_folder) / "assets" / pdf_basename
        if not image_folder.exists():
            os.makedirs(image_folder)
        return image_folder

    @staticmethod

    def extract_image_from_annot(rect, content, page, pdf_basename, notes_folder, image_counter):
        """Extracts an image from a given annotation.
        
        Args:
            rect: tuple or pymupdf.Rect of the annotation
            content: str, the content/comment of the annotation
            page: pymupdf.Page object
            pdf_basename: str name of pdf
            notes_folder: str/Path
            image_counter: int counter
        """
        zoom_x = 5.0  # horizontal zoom
        zoom_y = 5.0  # vertical zoom
        mat = pymupdf.Matrix(zoom_x, zoom_y)  # zoom factor 5 in each dimension

        clip = pymupdf.Rect(rect)
        pix = page.get_pixmap(matrix=mat, clip=clip)

        pix_text = (content or "").replace("\r", "\n")
        pix_lines = pix_text.splitlines()

        if pix_text == "":
            pix_title = str(image_counter)
            image_counter += 1
        else:
            pix_title = pix_lines[0].replace("#", "")
            # Sanitize filename
            pix_title = "".join(x for x in pix_title if x.isalnum() or x in (' ', '-', '_')).strip()

        image_folder = PdfUtils.get_image_folder(notes_folder, pdf_basename)
        nameImg = f"SS_{pdf_basename.replace(' ', '')}(pg{page.number + 1})_{pix_title.replace(' ', '')}.png"
        pix.save(image_folder / nameImg)

        return image_counter
