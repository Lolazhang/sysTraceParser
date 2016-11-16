from HTMLParser import HTMLParser
class traceParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.scriptTag=False
        self.index=0

    def handle_starttag(self,tag,attrs):
        #print "tag start",tag
        if tag=="script":
            self.scriptTag=True
            self.index+=1
            print "<script>"


    def handle_endtag(self,tag):
       # print  "end",tag
        if tag=="script":
            self.scriptTag=False
            print "</script>"
    def handle_data(self,data):
        if self.scriptTag==True:
            #print data
            data1=data
            f=file(str(self.index)+".js",'w')
            f.write(data)

parser=traceParser()

parser.feed(open("mynewtrace.html").read())