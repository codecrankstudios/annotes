########################## == USES GLOB == ########################################
# 
# FOR OBSIDIAN VAULT
# If Common Folder is turned on, it will create files in the specified directory.
# With checks for not annotated and modified files. Reduces run time.
###################################################################################

import glob
from pathlib import Path
import os
import fitz
from fitz.utils import getColor
import re
import datetime
import dateutil.relativedelta
import dateutil


##################### == Configurations == ##########################
## Customisations for obsidian specific settings
add_YAML = 1 # 0 for no, 1 for yes, to add frontmatter at top
add_date = 1 # 0 for no, 1 for yes, to add dates at top
annot_prefix = "&"
file_extn = ".md"
file_tags = ["source/annotes"]
# library_path = "Library/Alexandria"

### create files in a certain location
common_folder_flag = 0 # 0 for no, 1 for yes
common_folder_name = "Knowledge/Sources/Annotations" # folder in the root of the code
common_images_path = "Assets"


### Breadcrumbs Key and Value
parent_bc_key = "Parent"
parent_bc_value = "Sources - Annotations"


# define date in our format
now = datetime.datetime.now()
today = now.strftime("%Y-%m-%d %H:%M")
dated = now.strftime("%Y-%m-%d")
todayLongForm = now.strftime("%dth %B %Y, %A")
time = now.strftime("%H:%M")

# intersection threshold (_check_contain parameter)
_threshold_intersection = 0.5  # if the intersection is large enough.

######################## == Functions == ###############################

# write the YAML frontmatter (hidden in preview)
def YAML_writer(opened_file):
    opened_file.write("---\n")
    opened_file.write("title: & {}\n".format(basename))
    opened_file.write("source: {}\n".format(doc.name))
    opened_file.write("date: {}\n".format(today))
    opened_file.write("---\n\n")

# write obsidian wiki link to the pdf page
def file_link_to_page(basename, page):
    file_link = ("\n%%[[{}.pdf#page={}]]%%\n".format(basename, (page.number+1)))
    return file_link


#  Checks for intersections
def _check_contain(r_word, points):
    """If `r_word` is contained in the rectangular area.

    The area of the intersection should be large enough compared to the
    area of the given word.

    Args:
        r_word (fitz.Rect): rectangular area of a single word.
        points (list): list of points in the rectangular area of the
            given part of a highlight.

    Returns:
        bool: whether `r_word` is contained in the rectangular area.
    """
    # `r` is mutable, so everytime a new `r` should be initiated.
    r = fitz.Quad(points).rect
    r.intersect(r_word)

    if r.get_area() >= r_word.get_area() * _threshold_intersection:
        contain = True
    else:
        contain = False
    return contain

# extract words under the annotations
def _extract_annot(annot, words_on_page):
    """Extract words in a given highlight.

    Args:
        annot (fitz.Annot): [description]
        words_on_page (list): [description]

    Returns:
        str: words in the entire highlight.
    """
    quad_points = annot.vertices
    quad_count = int(len(quad_points) / 4)
    sentences = ['' for i in range(quad_count)]
    for i in range(quad_count):
        points = quad_points[i * 4: i * 4 + 4]
        words = [
            w for w in words_on_page if
            _check_contain(fitz.Rect(w[:4]), points)
        ]
        sentences[i] = ' '.join(w[4] for w in words)
    sentence = ' '.join(sentences)

    return sentence

# sort annotations 
def _sort_annots(page):
    s_annots = [a for a in page.annots()]
    s_annots.sort(key=lambda a: (a.rect.bl.y, a.rect.bl.x))
    return s_annots

def _print_ext_ind(annot,header_flag, basename, page, indent_flag):
    text = annot.info["content"]\
        .replace("\r", "\n")
    text_lines = text.splitlines()

    exclusions = [":", ",", ";","-","—", "―", "‖", "|"]
    
    # x = 0
    indent_count = 0
    if not annot.type[0] in (0, 2, 4, 5):
        extracthl = _extract_annot(annot, wordlist)

        # while extracthl.find("‖"):
        #     x == extracthl.index("‖")
        #     extracthl = extracthl.replace(extracthl[x], '', 1)

        while extracthl.startswith(tuple(exclusions)):
            extracthl = extracthl.replace(extracthl[0], '', 1)

        while extracthl.endswith(tuple(exclusions)):
            extracthl = extracthl.replace(extracthl[len(extracthl)-1:], '', 1)
            

    else: extracthl = ""
    
    x = re.search(r"^\(([a-z])\)", extracthl)
    if x: 
        return 0, 0


    if not text=="":
        # print("after text header_flag==",header_flag, basename, page, indent_flag)
        
        for tl in text_lines:

            if tl is text_lines[0]:  
                temp_slash = ""
                slash_flag = 0

                if tl.startswith('/') or tl.startswith('/ '): # add to line
                    tl = tl.replace('/ ', '',1).replace('/', '', 1)
                    slash_flag = 1
                    
                if tl.startswith('++') or tl.startswith('++ '): # add to line
                                    
                    tlm = tl.replace('++ ', '',1).replace('++', '', 1)
                    
                    if slash_flag ==1:
                        temp_slash = extracthl
                        extracthl = tlm
                        tlm = temp_slash

                    if header_flag==1:
                        # print("found header_flag ++", extracthl)
                        Annot_Doc.write("\n- {} {}".format(tlm, extracthl))
                        header_flag=0
                    else:
                        # print("found ++", extracthl)
                        Annot_Doc.write(" ... {} {}".format(tlm, extracthl))
                        header_flag=0
                    continue                    
                
                # case for multiple indents
                elif tl.startswith('+') or tl.startswith('+ '): # sub sub indents
                    # print("FOUND+")
                    header_flag = 0
                    tlm = tl.replace('+ ', '',1).replace('+', '', 1)

                    indent_count = 1

                    while tlm.startswith('-'):
                        tlm = tlm.replace('-', '', 1)
                        indent_count =indent_count + 1
                       
                    # print(indent_count)

                    if indent_count-indent_flag > 1 and indent_flag >= 0:
                        indent_count = indent_flag + 1
  
                    if slash_flag ==1:
                        temp_slash = extracthl
                        extracthl = tlm
                        tlm = temp_slash

                    if header_flag==1:
                        # print("FOund header_flag+ ", extracthl)
                        # Annot_Doc.write("\n- {} {}".format(tlm, extracthl))
                        indent_count=0
            

                    # elif indent_flag==0:
                    #     Annot_Doc.write("\n\t- {} {}".format(tlm, extracthl))
                    #     indent_flag=0

                    Annot_Doc.write("\n{}- {} {}".format(indent_count*"\t", tlm, extracthl))
                    indent_flag = indent_count


               
                # elif tl.startswith('+') or tl.startswith('+ '): # sub indents
                #     # print("FOUND+")
                #     tlm = tl.replace('+ ', '',1).replace('+', '', 1)
                #     if slash_flag ==1:
                #         temp_slash = extracthl
                #         extracthl = tlm
                #         tlm = temp_slash

                #     if header_flag==1:
                #         # print("FOund header_flag+ ", extracthl)
                #         Annot_Doc.write("\n- {} {}".format(tlm, extracthl))
                #         header_flag=0
                    
                #     else:
                #         # print("found zero header_flag +")
                #         Annot_Doc.write("\n\t- {} {}".format(tlm, extracthl))
                #         header_flag=0

                elif tl.startswith('#'):
                    indent_count = 0

                    if slash_flag ==1:
                        temp_slash = extracthl
                        extracthl = tl
                        tl = temp_slash
                        
                    # print("header")
                    header_flag = 1
                    Annot_Doc.write("\n\n{} {}".format(tl, extracthl))
                    # print("hello")
                    file_link = file_link_to_page(basename, page)
                    Annot_Doc.write(file_link)
                    

                else:
                    indent_count = 0
                    header_flag=0

                    if slash_flag ==1:
                        temp_slash = extracthl
                        extracthl = tl
                        tl = temp_slash

                    Annot_Doc.write("\n- {} {}".format(tl, extracthl))
                   

            else: # if the comment contains multiple lines (only in the case of pop-ups or standalone notes)
                if tl.startswith("    "):
                    Annot_Doc.write("\n{}".format(tl))
                    header_flag=0
                else: 
                    Annot_Doc.write("\n\t- {}".format(tl))
                    header_flag=0

        
    # When there is no comment at all, only HIGHLIGHT
    elif text=="" and annot.type[0] in (8,9):
        # highlighted text
        Annot_Doc.write("\n- {}".format(extracthl))
        header_flag=0
    indent_flag = indent_count
    return header_flag, indent_flag

def _print_img_ind(annot, header_flag, basename, foldername, image_foldername,  ranNum, page):
    # print("IMAGE IMAGE IMAGE")
    img_flag=1
    zoom_x = 5.0  # horizontal zoom
    zomm_y = 5.0  # vertical zoom
    mat = fitz.Matrix(zoom_x, zomm_y)  # zoom factor 5 in each dimension

    clip = fitz.Rect(annot.rect)
    pix = page.get_pixmap(matrix=mat, clip=clip)
    
    pix_text = annot.info["content"].replace("\r", "\n")
    
    pix_lines = pix_text.splitlines()
    

    if pix_text =='':
        pix_title= str(ranNum)
        ranNum += 1
    else: pix_title = pix_lines[0].replace("#", "")
    
    nameImg = "SS_{}(pg{})_{}.png".format(basename.replace(" ",""), (page.number+1), pix_title.replace(" ",""))
    pix.save(image_foldername/nameImg)
    # print(pix_title)

    Annot_Doc.write("\n\n---\n\n")

    if not pix_text=="":
        for pl in pix_lines:
            if pl==pix_lines[0]:
                if pl.startswith('#') or pl[0].startswith('-') or pl[0].startswith('- '):
                    Annot_Doc.write("\n{}".format(pl))
                    if pl.startswith('#'): Annot_Doc.write(file_link_to_page(basename, page))
                else: Annot_Doc.write("\n- {}".format(pl))

            elif pl.startswith('- ') or pl.startswith('    - '):
                Annot_Doc.write("\n\t{}".format(pl))  
            else:
                Annot_Doc.write("\n- {}".format(pl))

        Annot_Doc.write("\n\n\t![[{}]]".format(nameImg))
        file_link_to_page(basename, page)

    else:
        Annot_Doc.write("\n\n- [?] Title Missing\n\n\t![[{}]]".format(nameImg))
    return ranNum



def extract_prelims_test(filename):
    filename = Path(filename)
    basename = filename.stem
    # ofile = basename + ".md"
    doc = fitz.open(filename)
    # fout = open(ofile,  "w", encoding="utf-8")
    # p = fitz.Point(54, 100)
    QuesNo = []
    Ans  = []
    Marked = []
    Marks = []
    Total = 0
    Correct = 0
    Wrong = 0
    
    for l in range(100):
        Marked.append("-")
        Marks.append(0)
    
    # print(Marked)
    for page in doc:
        # p = fitz.Point(50, 72)  # start point of 1st line

        # text = "Some text,\nspread across\nseveral lines."
        # # the same result is achievable by
        # # text = ["Some text", "spread across", "several lines."]

        # rc = page.insert_text(p,  # bottom-left of 1st char
        #                     text,  # the text (honors '\n')
        #                     fontname = "helv",  # the default font
        #                     fontsize = 11,  # the default font size
        #                     rotate = 0,  # also available: 90, 180, 270
        #                     )
        # print("%i lines printed on page %i." % (rc, page.number))
        
        # fout.write(page.get_text().encode("utf-8") + bytes((12,)))
        a = page.get_text()
        wordlist = page.get_text("words")

        s_annots = [c for c in page.annots()]
        Ticks = []
        TicksRect = []
        Ques = []
        QuesRect = []
        ExtractedMarks = []
        dummyPDF = filename.parent/('Marked - '+filename.stem+'.pdf')
        doc.save(dummyPDF)

        for v, mark in enumerate(s_annots):
            if mark.type[0] in (8,9):
                extracthl = _extract_annot(mark, wordlist)
                m = s_annots[v].rect[0:4]
                # print(m)
                # print(s_annots[v], extracthl)
                x = re.search(r"^\(([a-d])\)", extracthl)
                if x:
                    Ticks.append(x.group(1).upper())
                    TicksRect.append(m)
            if mark.type[0] == 10:
                page.delete_annot(mark)
                doc.save(dummyPDF)
            # if mark.type[0] == 0 and mark.type["content"].startswith("  Your Answer: ("):
            #     page.delete_annot(mark)
            #     doc.save(dummyPDF)




        # print(page.number+1, Ticks)
        for b in wordlist:

            if b[-1] == 0:
                # fout.write(b[4])
                x = re.search(r"^([0-9]+)\.", b[4])
                if x and (b[0]<60 or 300 < b[0] < 330):
                    r = b[0:4]
                    Ques.append(x.group(1))
                    QuesRect.append(r)
                
        page_x = page.rect[2]/2
        page_y = page.rect[3]

        for num in range(len(Ques)):
                # print("Ques",Ques[num])
                flag = 0
                
                for mnum in range(len(Ticks)):
                    if flag == 1:
                        continue
                    # print("mnum num len(Ques):",mnum, num, len(Ques))
                    if (QuesRect[num][0] < TicksRect[mnum][0]  and # x-coord
                        TicksRect[mnum][1] > QuesRect[num][1]
                        ):
                            # print("num and len", num, " ", len(Ques))

                            if (num < len(Ques)-1 and
                                TicksRect[mnum][1] < QuesRect[num+1][1] and
                                TicksRect[mnum][0] < page_x
                            ):
                                # print("    > Found in First Quad", Ques[num], Ticks[mnum])
                                Marked[int(Ques[num])-1] = Ticks[mnum]
                                flag = 1
                            
                            elif (num < len(Ques)-1 and
                                QuesRect[num+1][3] < QuesRect[num][3] and
                                QuesRect[num][1] > QuesRect[num-1][1] and
                                TicksRect[mnum][0] < page_x
                            ):
                                # print("    > Found in Second Quad", Ques[num], Ticks[mnum])
                                Marked[int(Ques[num])-1] = Ticks[mnum]
                                flag = 1
                            
                            elif (num < len(Ques)-1 and
                                TicksRect[mnum][1] < QuesRect[num+1][1] and
                                TicksRect[mnum][0] > page_x and QuesRect[num][0] > page_x
                            ):
                                # print("    > Found in Third Quad", Ques[num], Ticks[mnum])
                                Marked[int(Ques[num])-1] = Ticks[mnum]
                                flag = 1
                            
                            elif (num == len(Ques)-1 and
                                TicksRect[mnum][1] < page_y
                                ):
                                # print("    > Found in Fourth Quad", Ques[num], Ticks[mnum])
                                Marked[int(Ques[num])-1] = Ticks[mnum]
                                flag = 1
                            
                            
        
        # PagesToMark = [] 
        QuesToMark = []
        ### ANSWERSHEET
        tl = a.splitlines()
        for line in tl:
            # x = re.search(r"^([0-9]+)\. \n", line)
            y = re.search(r"^Q ([0-9]+).([A-Z])", line)

            # if x:
            #     print(x.group())
            if y:
                # print(x.group())
                SolutionPages = page.number
                QuesNo.append(y.group(1))
                Ans.append(y.group(2))

                # print(line)
                              
                
                # QuesToMark.append(rl)
                # PagesToMark.append(page)
                QN = int(y.group(1))
                

                if Marked[(QN) - 1] == y.group(2):
                    # print(QN, Marked[QN - 1], y.group(2), "Correct")
                    Marks[QN-1] = 2
                    Total = Total + 2
                    Correct = Correct + 1

                elif not Marked[QN -1] == "-":
                    # print(QN, Marked[QN - 1], y.group(2), "Wrong")
                    Marks[QN-1] = -0.66
                    Total = Total - 0.66
                    Wrong = Wrong + 1
                    # print(PagesToMark[QN-1])
                    rl = page.search_for(line, quads= True)
                    # p = rl[0][3]
                    # text = "  Your Answer: (" + Marked[QN-1] + ")"
                    page.add_squiggly_annot(rl)   
                    # page.insert_text(p,  # bottom-left of 1st char
                    #     text,  # the text (honors '\n')
                    #     fontname = "helv",  # the default font
                    #     fontsize = 10,  # the default font size
                    #     rotate = 0,  # also available: 90, 180, 270
                    #     color = getColor("red"),
                    # )
                    doc.save(dummyPDF)

                # QuesToMark.append(rl)
        
                # print("THE QUAD: ", QuesToMark)

    # print(PagesToMark)       
    
    # # MArks CALCULATION
   

    # for i, e in enumerate(QuesNo):
    #     if Ans[i] == Marked[i]:
    #         Marks[i] = 2
    #         Total = Total + 2
    #         Correct = Correct + 1

    #     elif not Marked[i] == "-":
    #         Marks[i] = -0.66
    #         Total = Total - 0.66
    #         Wrong = Wrong + 1
    #         print(PagesToMark[i])
    #         PagesToMark[i].add_squiggly_annot(QuesToMark[i])   
    #         doc.save(filename)

    return QuesNo, Ans, Marked, Marks, [Correct, Wrong, Correct+Wrong, Total]
    
    




########################## == Main Code Starts Here == ##################################

# read files in the folder
for filename in glob.glob("**/*.pdf", recursive=True):
    # if not filename.endswith(".pdf"):
    #     continue #exclude files other than PDFs
   
    # open PDF in MuPDF
    doc = fitz.open(filename)
    print("\n\nPDF Name:", doc.name)

    # Identify only the files which have annotations, ignore the rest
    r_annots = []
    edited_flag=0

    
    for page in doc:
        r_annots = _sort_annots(page)
        if r_annots:
            edited_flag = 1
            break
    
    if edited_flag == 0:
        print("          >> No Annotations Found")
        continue

    

    # Get the name of the file without any extentions
    filename = Path(filename)
    basename = filename.stem
    # print(basename)

    if basename.startswith("Marked -"): 
        print("          >> Marked PDF; Not Extracting")
        continue
    vaultroot = Path(__file__).parent.parent.parent
    # print("Vault", vaultroot)
    # Name of the sub-folder with the files for a pdf
    if common_folder_flag:
        foldername = vaultroot/common_folder_name
        image_foldername = foldername/common_images_path
    else: 
        foldername = filename.parent/(annot_prefix + ' ' + basename)
        image_foldername = foldername

    doc_create_flag = 0
    # create folder for the file selected if not already present
    if not foldername.exists():
        os.makedirs(foldername)
        doc_create_flag = 1

    # path for the new annotations file for the PDF
    annot_doc_path = foldername/(annot_prefix+' '+ basename + file_extn)

   
        # for index, annot in enumerate(r_annots):
        #     if annot.type[0] in (0, 2, 8, 9, 16, 4,5):
        #         print(r_annots)
    # compare for modified timings of PDF and Annot Doc
    if doc_create_flag == 0:
        file_mtime = os.stat(filename)[8]
        doc_mtime= os.stat(annot_doc_path)[8]
        file_mtime  = datetime.datetime.fromtimestamp(file_mtime)
        doc_mtime  = datetime.datetime.fromtimestamp(doc_mtime)

        # print(file_mtime, doc_mtime)

        diff = dateutil.relativedelta.relativedelta (file_mtime, doc_mtime)

        print("          >> Already Extracted. Checking for modified time ....\n          >> Modified time (PDF - Doc) : ", diff)

        if diff.months<0 or diff.days < 0 or diff.hours < 0 or diff.minutes < 0 or diff.seconds<0:
            print("          >> No need for extraction. PDF not modified after the last extraction.")
            continue

    # open the Annot_Doc
    Annot_Doc = open(annot_doc_path, "w", encoding="utf-8")

    
    print("          >> Extracting . . . . . \n")
    # Write YAML if enabled
    if add_YAML==1:
        YAML_writer(Annot_Doc)

    # add tags to the Annot_Doc before H1
    for t in file_tags:
        Annot_Doc.write("#{} ".format(t))
    
    # add Parent for BreadCrumbs
    Annot_Doc.write("\n**{}**::[[{}]]\n".format(parent_bc_key, parent_bc_value))

    # add title to the Annot_Doc -> Header 1
    Annot_Doc.write("# & {}\n\n".format(basename))

    
    

    
    
    x = re.search(r"(202[0-9])VPT([0-9]+)", basename)
    if x: 
               
        Q, A, M, Ma, Analysis = extract_prelims_test(filename)
        os.remove(filename) 
        # print("deleted")
        os.rename(str(filename.parent/('Marked - ' + filename.stem+ '.pdf')), str(filename))
        # print("renamed")

        # admonition block
        Annot_Doc.write("> [!info: Details]\n")
        Annot_Doc.write("> Title:: & {}\n".format(basename))
        Annot_Doc.write("> Publisher:: VisionIAS\n")
        Annot_Doc.write("> Type:: Prelims\n")
        Annot_Doc.write("> Year:: {}\n".format(x.group(1)))
        Annot_Doc.write("> Pages:: {}\n".format(doc.page_count))
        Annot_Doc.write("> Test Code:: \n")
        Annot_Doc.write("> Test Number:: {}\n".format(x.group(2)))
        Annot_Doc.write("> Subject:: \n")
        Annot_Doc.write("> Status:: 🟢\n")
        Annot_Doc.write("> PDF:: [[{}.pdf]]\n".format(basename))
        

        Annot_Doc.write("\n---\n")


        Annot_Doc.write("\n#source/upsc/test/marksheet\n\n## Marks and Analysis\n")

        Annot_Doc.write("\n- **Date of Test**:: {}".format(dated))
        Annot_Doc.write("\n- **Marks**:: {:.2f}".format(Analysis[3]))
        Annot_Doc.write("\n- **Attempted**:: {}".format(Analysis[2]))
        Annot_Doc.write("\n- **Correct**:: {}".format(Analysis[0]))
        Annot_Doc.write("\n- **Wrong**:: {}".format(Analysis[1]))

        Annot_Doc.write("\n\n\n```ad-table\ntitle: Key and Marksheet\n")
        Annot_Doc.write("collapse: true\n")
        Annot_Doc.write("|Question|Answer|Marked|Marks|\n")
        Annot_Doc.write("|:---:|:---:|:---:|:---:|\n")
        for i, e in enumerate(Q):
            Annot_Doc.write("|  {}  |  {}  |  {}  |{}|\n".format(Q[i], A[i], M[i], Ma[i]))
            # print("|{}|{}|{}|\n".format(QuesNo[i], Ans[i], Marked[i]))
        
        Annot_Doc.write("|Correct: {}|Wrong: {}|Unattemped: {}|Total: {:.2f}|\n".format(Analysis[0], Analysis[1], 100 - Analysis[0] - Analysis[1], Analysis[3]))
        Annot_Doc.write("```")
    
    else: 
        # admonition block
        Annot_Doc.write("> [!info: Details]\n")
        Annot_Doc.write("> Title:: & {}\n".format(basename))
        Annot_Doc.write("> Pages:: {}\n".format(doc.page_count))
        Annot_Doc.write("> PDF:: [[{}.pdf]]\n".format(basename))
        Annot_Doc.write("\n---\n")

    
    Annot_Doc.write("\n\n\n# Annotations\n\n")

    

    # loop to flip through the pages
    for page in doc:

        # extract the word list from the page
        wordlist = page.get_text("words")
        # print("\n-—--—--—--—---\nPAGE: ", page.number)
        # print(wordlist)

        # random number for the image naming (resets every page)
        ranNum = 1

        # sort the annotations in the page
        s_annots = _sort_annots(page)


        header_flag = 0 # header_flag for chekcing if previous annot is header or not
        img_ind = []
        ext_ind = []
        inc_ind = []
        inc_mat = []
        
        ### Identify image objects
        for index, annot in enumerate(s_annots):
            if annot.type[0] in (4,5):
                img_ind.append(index)
            

        ### Identify the highlights inside image boxes
        for index, annot in enumerate(s_annots):
            # print("Index:  ", index, " " ,annot.type[0])
            if annot.type[0] in (0, 2, 8, 9, 16):
                for i in img_ind: 

                    # print("I == ", i)
                    if s_annots[i].rect.contains(annot.rect):
                        # print(index, "match",i)
                        # print(extracthl)
                        inc_ind.append(index)
                        inc_mat.append((i, index))
                        # print(index, "inccc", inc_ind)
                        
                    
                if not index in inc_ind:
                    ext_ind.append(index)
                    # print(index, "extttt", ext_ind)
            else: continue

        ### Print in the MD File

        a = [0,0]

                    
        for ext in ext_ind:
            # print("ext  ", ext)
            header_flag = a[0]
            indent_flag = a[1]


            # print("intoooo annot")\
            a = _print_ext_ind(s_annots[ext],header_flag, basename, page, indent_flag)

        for img in img_ind:
            # print("PREV img", img)
            ranNum = _print_img_ind(s_annots[img], header_flag, basename, foldername, image_foldername,  ranNum, page)

            for inc in inc_ind:
                # print("img: ", img, " inc: ", inc, "in", inc_ind)
                if (img, inc) in inc_mat:
                    _print_ext_ind(s_annots[inc],header_flag, basename, page, indent_flag)
            Annot_Doc.write("\n---\n")


    Annot_Doc.close() 
# doc.saveInc(doc.name)
doc.close


