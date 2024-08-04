def get_file_extension(text):
    if "python file" in text:
        ex = ".py"
    elif "java file" in text:
        ex = ".java"
    elif "text file" in text:
        ex = ".txt"
    elif "html file" in text:
        ex = ".html"
    elif "css file" in text:
        ex = ".css"
    elif "javascript file" in text:
        ex = ".js"
    elif "json file" in text:
        ex = ".json"
    elif "xml file" in text:
        ex = ".xml"
    elif "csv file" in text:
        ex = ".csv"
    elif "markdown file" in text:
        ex = ".md"
    elif "yaml file" in text:
        ex = ".yaml"
    elif "image file" in text:
        ex = ".jpg"  # You can add more image extensions if needed
    elif "video file" in text:
        ex = ".mp4"  # You can add more video extensions if needed
    elif "audio file" in text:
        ex = ".mp3"  # You can add more audio extensions if needed
    elif "pdf file" in text:
        ex = ".pdf"
    elif "word file" in text:
        ex = ".docx"
    elif "excel file" in text:
        ex = ".xlsx"
    elif "powerpoint file" in text:
        ex = ".pptx"
    elif "zip file" in text:
        ex = ".zip"
    elif "tar file" in text:
        ex = ".tar"
    else:
        ex = ""  # Default case if no match found
    return ex

def update_text(text):
    if "python file" in text:
        text = text.replace("python file", "")
    elif "java file" in text:
        text = text.replace("java file", "")
    elif "text file" in text:
        text = text.replace("text file", "")
    elif "html file" in text:
        text = text.replace("html file", "")
    elif "css file" in text:
        text = text.replace("css file", "")
    elif "javascript file" in text:
        text = text.replace("javascript file", "")
    elif "json file" in text:
        text = text.replace("json file", "")
    elif "xml file" in text:
        text = text.replace("xml file", "")
    elif "csv file" in text:
        text = text.replace("csv file", "")
    elif "markdown file" in text:
        text = text.replace("markdown file", "")
    elif "yaml file" in text:
        text = text.replace("yaml file", "")
    elif "image file" in text:
        text = text.replace("image file", "")
    elif "video file" in text:
        text = text.replace("video file", "")
    elif "audio file" in text:
        text = text.replace("audio file", "")
    elif "pdf file" in text:
        text = text.replace("pdf file", "")
    elif "word file" in text:
        text = text.replace("word file", "")
    elif "excel file" in text:
        text = text.replace("excel file", "")
    elif "powerpoint file" in text:
        text = text.replace("powerpoint file", "")
    elif "zip file" in text:
        text = text.replace("zip file", "")
    elif "tar file" in text:
        text = text.replace("tar file", "")
    else:
        pass
    return text



def create_file(text):
    selected_ex = get_file_extension(text)
    text = update_text(text)
    if "named" in text or "with name" in text:
        text = text.replace("named","")
        text = text.replace("with name","")
        text = text.replace("create","")
        text = text.strip()
        with open(f"{text}{selected_ex}","w"):
            pass
    else :
        with open(f"demo{selected_ex}","w"):
            pass

