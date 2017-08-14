from cStringIO import StringIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import os
import sys, getopt
import re
import numpy as np
from moviepy.editor import *
from gtts import gTTS
from nltk.corpus import stopwords 
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tag import pos_tag
import string
import gensim
from gensim import corpora
import google_image_download as image_downloader
import shutil

stop = set(stopwords.words('english'))
lemma = WordNetLemmatizer()
_FPS=24

f_dict = open('dictionary.txt')# from scrabble words list
scrabble_list = []
for line in f_dict:
    scrabble_list.append(str(line.replace('\n','').lower()))
f_dict.close()
# print scrabble_list
print "scrabble_list loaded!"



#converts pdf, returns its text content as a string
def convert_pdf_to_txt(fname, pages=None):
    if not pages:
        pagenums = set()
    else:
        pagenums = set(pages)

    output = StringIO()
    manager = PDFResourceManager()
    converter = TextConverter(manager, output, laparams=LAParams())
    interpreter = PDFPageInterpreter(manager, converter)

    infile = file(fname, 'rb')
    for page in PDFPage.get_pages(infile, pagenums):
        interpreter.process_page(page)
    infile.close()
    converter.close()
    text = output.getvalue()
    output.close
    print "conversion from PDF to TXT done!\n"
    return text 

def convert_txt_to_clean(fname):
    fr = open('./txt/'+fname[:-4]+'.txt')
    full_text = ''
    for line in fr:
        if line == '\n':
            full_text += line + '\n'
            continue
        line = line.replace('\n','')
        line = re.sub(r"[^a-zA-Z0-9'\".,!-]+", ' ', line)
        if len(line) > 3:
            full_text += line+' '
    # print full_text
    fr.close()
    fw = open('./txt/'+fname[:-4]+'_clean.txt', 'w') # final text final is stored as filename_clean.txt
    fw.write(full_text.replace('Fig.', 'Figure'))
    fw.close()
    print "conversion from TXT to Clean TXT done!\n"

def format_text(string): #break in to lines to fit the screen
    words=string.split()
    output=''
    buffer_string=''
    for w in words:
        if(len(buffer_string)<50):
            buffer_string+=w+' '
        else:
            output+=buffer_string+'\n'
            buffer_string=w+' '
    output+=buffer_string   
    return output

def clean_txt_to_clean_words(doc):
    global scrabble_list
    doc = doc.replace(',', ' ')
    propernouns = doc.lower().split()
    propernouns_clean = [word for word in propernouns if (word not in scrabble_list)]
    propernouns_string = ' '.join(propernouns_clean)
    stop_free = " ".join([i for i in propernouns_string.split() if i not in stop])
    normalized = " ".join(lemma.lemmatize(word) for word in stop_free.split())
    return normalized


def get_topics_from_text(line):
    doc_complete = line.split('.')
    doc_clean = [clean_txt_to_clean_words(doc).split() for doc in doc_complete]# ignore if length of docs for topic analysis is less than 3        
    doc_clean_empty = True
    all_topics = []
    for doc in doc_clean:
        if len(doc) > 0:
            doc_clean_empty = False
    if len(doc_clean) >=1 and doc_clean_empty == False:
        dictionary = corpora.Dictionary(doc_clean)
        doc_term_matrix = [dictionary.doc2bow(doc) for doc in doc_clean]
        Lda = gensim.models.ldamodel.LdaModel
        num_topics = 3
        ldamodel = Lda(doc_term_matrix, num_topics=num_topics, id2word = dictionary, passes=25)
        # print '\n\n',doc_complete
        # print '\n',doc_clean, '\n'
        # print ldamodel.print_topics(num_topics=5, num_words=2), '\n\n'
        for i in range(0,num_topics):
            topic = ldamodel.get_topic_terms(i, topn=2)
            topic_list = []
            for word in topic:
                word_name = dictionary.get(word[0])
                if len(word_name) > 1:
                    topic_list.append(word_name)
            topic_list.sort()
            topic_name = " ".join(topic_list)
            add = False
            for ch in topic_name:# ignore numerical topics
                if ch in r"[abcdefghijklmnopqrstuvwxyz]":
                    add = True
            if add:
                if topic_name not in all_topics:
                    all_topics.append(str(topic_name))

    return all_topics

def get_topics_from_text1(line):
    doc_complete = line.split('.')
    doc_clean = [clean_txt_to_clean_words(doc).split() for doc in doc_complete]# ignore if length of docs for topic analysis is less than 3        
    doc_clean_empty = True
    doc_total_list = []
    all_topics = []
    for doc in doc_clean:
        if len(doc) > 0:
            doc_clean_empty = False
    if len(doc_clean) >=1 and doc_clean_empty == False:
        for doc in doc_clean:
            doc_total_list = doc_total_list + doc

    print " important word list: ", doc_total_list
    for i in range(0,len(doc_total_list),2):
        if i+2<len(doc_total_list):
            if (str(doc_total_list[i]) == str(doc_total_list[i+1])) and (str(doc_total_list[i+2]) == str(doc_total_list[i+1])) :
                topic_name = (doc_total_list[i+2])            
            elif str(doc_total_list[i]) == str(doc_total_list[i+1]):
                topic_name = (' '.join([doc_total_list[i],doc_total_list[i+2]]))
            elif str(doc_total_list[i+1]) == str(doc_total_list[i+2]):
                topic_name = (' '.join([doc_total_list[i],doc_total_list[i+1]]))
            elif str(doc_total_list[i]) == str(doc_total_list[i+2]):
                topic_name = (' '.join([doc_total_list[i],doc_total_list[i+1]]))
            else:
                topic_name = (' '.join([doc_total_list[i],doc_total_list[i+1],doc_total_list[i+2]]))
            add = False
            for ch in topic_name:# ignore numerical topics
                if ch in r"[abcdefghijklmnopqrstuvwxyz]":
                    add = True
            if add:
                if topic_name not in all_topics:
                    all_topics.append(str(topic_name))

        elif i+1<len(doc_total_list):
            if str(doc_total_list[i]) == str(doc_total_list[i+1]):
                topic_name = (doc_total_list[i])
            else:
                topic_name = (' '.join([doc_total_list[i],doc_total_list[i+1]]))
            add = False
            for ch in topic_name:# ignore numerical topics
                if ch in r"[abcdefghijklmnopqrstuvwxyz]":
                    add = True
            if add:
                if topic_name not in all_topics:
                    all_topics.append(str(topic_name))

    return all_topics






path = raw_input("PATH TO PDF FILE: ")
infile = path.split('/')[-1]

full_text_messy = convert_pdf_to_txt(infile)
fw = open('./txt/'+infile[:-4]+'.txt', 'w')
fw.write(full_text_messy)
fw.close()

convert_txt_to_clean(infile)

audio_dir = './audio/tmp'
picture_dir = './picture/tmp'
video_dir = './video/tmp'
if os.path.exists(audio_dir):
    shutil.rmtree(audio_dir)
if os.path.exists(picture_dir):
    shutil.rmtree(picture_dir)
if os.path.exists(video_dir):
    shutil.rmtree(video_dir)


fr = open('./txt/'+infile[:-4]+'_clean.txt')
count_lines = 1
for line in fr:
    line = line.replace('\n','')
    all_topics = get_topics_from_text1(line)
    print '\n\n',line,'\n'
    print "all topics ", all_topics, '\n\n'
    folder_names = []
    for i in range(0,len(all_topics)):
        if len(all_topics) > 4:
            image_downloader.download_images(all_topics[i],1)
        else:
            image_downloader.download_images(all_topics[i],2)
        folder_names.append(all_topics[i].replace(' ','_'))

    text_sentences=[f for f in line.split('.') if len(f)>1]
    if len(text_sentences) <=0:
        continue

    if not os.path.exists(audio_dir):
        os.mkdir(audio_dir)
    if not os.path.exists(picture_dir):
        os.mkdir(picture_dir)
    if not os.path.exists(video_dir):
        os.mkdir(video_dir)

    print "creating "+str(len(text_sentences))+" audio files "
    for i in range(0,len(text_sentences)):
        tts = gTTS(text=text_sentences[i], lang='en', slow=False)
        tts.save(audio_dir+'/'+str(i)+'.mp3')
        print '\n',text_sentences[i],'\n'
        print "created "+ str(i)+ " audio file"

    text_clip_list=[]
    audio_clip_list=[]
    silence = AudioFileClip('./audio/silence.mp3').subclip(0,0.1)
    audio_clip_list.append(silence)
    for i in range(0,len(text_sentences)):
        sent_audio_clip=AudioFileClip(audio_dir+'/'+str(i)+'.mp3')
        print "length of audio: "+str(i)+" = ",sent_audio_clip.duration
        audio_clip_list.append(sent_audio_clip)
        sent_txt_clip = TextClip(format_text(text_sentences[i]),font='Courier-Bold',fontsize=200,color='yellow',bg_color='black',stroke_width=30).set_pos('bottom').set_duration(sent_audio_clip.duration).resize(width=1000)
        text_clip_list.append(sent_txt_clip)

    audio_clip=concatenate_audioclips(audio_clip_list)
    
    file_names = []
    for i in range(0,len(folder_names)):
        files = (fn for fn in os.listdir(picture_dir+'/'+folder_names[i]) if fn.endswith('.jpg') or fn.endswith('.png') or fn.endswith('.PNG') or fn.endswith('.JPG') or fn.endswith('.jpeg') or fn.endswith('.JPEG'))
        for file in files:
            file_names.append(folder_names[i]+'/'+file)

    # s_file_names = sorted(file_names, key=lambda x: x.split('.')[0].split('/')[1])
    s_file_names = file_names
    number_of_images=len(s_file_names)
    print s_file_names


    # minimum_image_size=1200
    video_clip_list=[]
    black_clip=ImageClip('./picture/black1.jpg').set_duration(0.1).set_fps(_FPS)
    video_clip_list.append(black_clip)
    black = './picture/black1.jpg'
    title_clip_list = []
    if number_of_images > 0:
        for f in s_file_names:
            temp_clip=ImageClip(picture_dir+'/'+f).set_duration(audio_clip.duration/number_of_images).set_position('center').set_fps(_FPS).crossfadein(0.5)
            name_txt_clip = TextClip(format_text(' '.join([word[:1].upper()+word[1:] for word in f.split('/')[0].split('_')])),font='Courier-Bold',fontsize=200,color='yellow',bg_color='black',stroke_width=30).set_position('top').set_duration(audio_clip.duration/number_of_images).resize(height=30)
            title_clip_list.append(name_txt_clip)
            # temp_clip = CompositeVideoClip([temp1_clip,name_txt_clip])
            video_clip_list.append(temp_clip)
            # minimum_image_size=min([minimum_image_size,temp_clip.size[0]])
            print 'temp_clip width: ',temp_clip.size
    else:
        temp_clip=ImageClip(black).set_duration(audio_clip.duration).set_fps(_FPS)
        video_clip_list.append(temp_clip)
        # minimum_image_size=min([minimum_image_size,temp_clip.size[0]])

    video_clip = concatenate_videoclips(video_clip_list).set_position('center')
    
    # print "Minimnum image size: "+str(minimum_image_size)
    # minimum_image_size = 0.98*minimum_image_size

    # resize_text_clip_list = []    
    # for sent_txt_clip in text_clip_list:
    #     resize_text_clip_list.append(sent_txt_clip.resize(width=minimum_image_size))
    txt_clip=concatenate_videoclips(text_clip_list).set_position('bottom')
    if len(title_clip_list) > 0:
        title_clip = concatenate_videoclips(title_clip_list).set_position('top')
        result=CompositeVideoClip([video_clip,txt_clip,title_clip])
    else:
        result=CompositeVideoClip([video_clip,txt_clip])

    print "Composite video clip size: ",result.size

    result_with_audio=result.set_audio(audio_clip)

    # print txt_clip.duration
    # print txt_clip.fps
    # print audio_clip.duration
    print "audio duration: "+str(audio_clip.duration)
    print "result duration: "+str(result.duration)
    print "result audio duration: "+str(result_with_audio.duration)
    # print video_clip.fps
    # print len(video_clip_list)

    result_with_audio.write_videofile(video_dir+'/'+str(count_lines)+'.mp4',codec='libx264',fps=_FPS)
    count_lines += 1

    shutil.rmtree(audio_dir)
    shutil.rmtree(picture_dir)


fr.close()

video_files = [fn for fn in os.listdir(video_dir) if fn.endswith('.mp4')]
video_files = sorted(video_files, key=lambda x: int(x.split('.')[0]))
video_clip_list = []
for video in video_files:
    clip = VideoFileClip(video_dir+'/'+video).crossfadein(0.5)
    video_clip_list.append(clip)

video_clip = concatenate_videoclips(video_clip_list)
video_clip.write_videofile(infile[:-4]+'.mp4',codec='libx264',fps=_FPS)


# shutil.rmtree(video_dir)



