import re
class AlertInfo:
    def __init__(self,alertinfo,start,events,args,tag):
        self.alertinfo=alertinfo
        self.events=events
        self.start=start
        self.alertTag=tag

        self.args=args
class Alerts:
    def __init__(self,frameunit):
        self.frameunit=frameunit
        self.alerts=[]

    def Checking(self):
        ret1=self.getBlockingGcAlert()
        ret2=self.getListViewAlert()
        ret3=self.getLockContentionAlert()
        ret4=self.getMeasureLayoutAlert()
        ret5=self.getPathAlert()
        ret6=self.getSaveLayerAlerts()
        ret7=self.getSchedulingAlert()
        ret8=self.getUploadAlert()
        ret9=self.getViewDrawAlert()
        self.alerts.extend(ret1)
        self.alerts.extend(ret2)
        self.alerts.extend(ret3)
        self.alerts.extend(ret4)
        self.alerts.extend(ret5)
        self.alerts.extend(ret6)
        self.alerts.extend(ret7)
        self.alerts.extend(ret8)
        self.alerts.extend(ret9)
        return self.alerts



    def getSaveLayerAlerts(self):
        ret=[]

        badAlphaRegEx = "^ (. +) alpha caused(unclipped)?saveLayer(\d +)x(\d +)$"
        pattern1=re.compile(badAlphaRegEx)
        saveLayerRegEx = "^ (unclipped)?saveLayer(\d +)x(\d +)$"
        pattern2=re.compile(saveLayerRegEx)
        viewAlertInfo="Inefficient View alpha usage', 'Setting an alpha between 0 and 1 has significant performance costs, if one of the fast alpha paths is not used."
        saveLayerAlertInfo="Expensive rendering with Canvas#saveLayer()', 'Canvas#saveLayer() incurs extremely high rendering cost. They disrupt the rendering pipeline when drawn, forcing a flush of drawing content. Instead use View hardware layers, or static Bitmaps. This enables the offscreen buffers to be reused in between frames, and avoids the disruptive render target switch."
        events=[]
        starts=[]
        for event in self.frameunit.events:
            name1=event.name
            name2=event.event.task.name
            if pattern1.match(name1) or pattern1.match(name2):
                alert=AlertInfo(viewAlertInfo,event.interval.start,[event],"","SaveLayerAlert")
                ret.append(alert)
            elif pattern2.match(name1) or pattern2.match(name2):
                starts.append(event.interval.start)
                events.append(event)
        if len(events)>len(ret):
            events.append(self.frameunit.ui_thread)
            starts.append(self.frameunit.ui_thread.interval.start)
            ret.append(AlertInfo(saveLayerAlertInfo,min(starts),events,"SaveLayerAlert"))

        return ret
    def getPathAlert(self):
        pathAlertInfo="Path texture churn', 'Paths are drawn with a mask texture, so when a path is modified / newly drawn, that texture must be generated and uploaded to the GPU. Ensure that you cache paths between frames and do not unnecessarily call Path#reset(). You can cut down on this cost by sharing Path object instances between drawables/views."
        events=[]
        starts=[]
        pattern=re.compile("^Generate Path Texture$")
        duration=0
        for event in self.frameunit.events:
            name1=event.name
            name2=event.event.task.name
            if name1=="Generate Path Texture" or name2=="Generate Path Texture":
                events.append(event)
                starts.append(event.interval.start)
                duration+=event.interval.duration
        if duration<0.003: ## 3 ms
            return []
        events.append(self.frameunit.ui_thread)
        return [AlertInfo(pathAlertInfo,min(starts),events,"Time Spent:"+str(duration),"PathAlert")]

    def getUploadAlert(self):
        pattern=re.compile("^Upload (\d+)x(\d+) Texture$")
        uploadAlertInfo="Expensive Bitmap uploads', 'Bitmaps that have been modified / newly drawn must be uploaded to the GPU. Since this is expensive if the total number of pixels uploaded is large, reduce the amount of Bitmap churn in this animation/context, per frame."
        starts=[]
        duration=[]
        events=[]
        for event in self.frameunit.events:
            name1=event.name
            name2=event.event.task.name
            if pattern.match(name1) or pattern.match(name2):
                events.append(event)
                starts.append(event.interval.start)
                duration+=event.interval.duration
        if len(events)==0 or duration<0.003:
            return []
        events.append(self.frameunit.ui_thread)
        return [AlertInfo(uploadAlertInfo,min(starts),events,"Time Spent:"+str(duration),"UploadAlert")]

    def getListViewAlert(self):
        listviewInflateAlertInfo="Inflation during ListView recycling', 'ListView item recycling involved inflating views. Ensure your Adapter#getView() recycles the incoming View, instead of constructing a new one."
        listviewBindAlertInfo="Inefficient ListView recycling/rebinding', 'ListView recycling taking too much time per frame. Ensure your Adapter#getView() binds data efficiently."
        events=[]
        duration=0
        starts=[]
        for event in self.frameunit.events:
            name1=event.name
            name2=event.event.task.name
            if name1 in ["obtainView","setupListItem"] or name2 in ["obtainView","setupListItem"]:
                events.append(event)
                starts.append(event.interval.start)
                duration+=event.interval.duration
        if len(events)==0 or duration<0.003:
            return []
        events.append(self.frameunit.ui_thread)
        return [AlertInfo(listviewBindAlertInfo,min(starts),events,"Time Spent:"+str(duration),"ListViewAlert")]
    def getMeasureLayoutAlert(self):
        measureLayoutAlertInfo="Expensive measure/layout pass', 'Measure/Layout took a significant time, contributing to jank. Avoid triggering layout during animations."
        events=[]
        starts=[]
        duration=0
        for event in self.frameunit.events:
            name1=event.name
            name2=event.event.task.name
            if name1 in ["measure","layout"] or name2 in ["measure","layout"]:
                events.append(event)
                starts.append(event.interval.start)
                duration+=event.interval.duration
        if len(events)==0 or duration<0.003:
            return []
        events.append(self.frameunit.ui_thread)
        return [AlertInfo(measureLayoutAlertInfo,min(starts),events,"Time Spent:"+str(duration),"MeasureLayoutAlert")]

    def getViewDrawAlert(self):
        viewDrawAlertInfo="Long View#draw()', 'Recording the drawing commands of invalidated Views took a long time. Avoid significant work in View or Drawable custom drawing, especially allocations or drawing to Bitmaps."
        events=[]
        starts=[]
        target=-1
        duration=0
        for event in self.frameunit.events:
            name1=event.name
            name2=event.event.task.name
            if name1 in ["getDisplayList","Record View#draw()"] or name2 in  ["getDisplayList","Record View#draw()"] :
                #events.append(event)

                duration+=event.interval.duration
                target=event
                break
        if duration<0.003:
            return []
        return [AlertInfo(viewDrawAlertInfo,target.interval.start,[target],"Time Spent:"+str(duration),"ViewDrawAlert")]

    def getBlockingGcAlert(self):
        blockingGcAlertInfo="Blocking Garbage Collection', 'Blocking GCs are caused by object churn, and made worse by having large numbers of objects in the heap. Avoid allocating objects during animations/scrolling, and recycle Bitmaps to avoid triggering garbage collection."
        events=[]
        starts=[]
        duration=0
        for event in self.frameunit.events:
            name1=event.name
            name2=event.event.task.name
            if name1 in ["DVM Suspend","GC: Wait For Concurrent"] or name2 in ["DVM Suspend","GC: Wait For Concurrent"]:
                events.append(event)
                starts.append(event.interval.start)
                duration+=event.interval.duration
        if duration<0.003 :
            return []
        events.append(self.frameunit.ui_thread)
        return [AlertInfo(blockingGcAlertInfo,min(starts),events,"Blocked Duration:"+str(duration),"BlockingGcAlert")]
    def getLockContentionAlert(self):
        lockContentionAlertInfo="Lock contention', 'UI thread lock contention is caused when another thread holds a lock that the UI thread is trying to use. UI thread progress is blocked until the lock is released. Inspect locking done within the UI thread, and ensure critical sections are short."
        events=[]
        starts=[]
        duration=0
        pattern=re.compile("^Lock Contention on ")
        for event in self.frameunit.events:
            name1=event.name
            name2=event.event.task.name
            if pattern.match(name1) or pattern.match(name2):
                events.append(event)
                starts.append(event.interval.start)
                duration+=event.interval.duration
        if duration<0.001:
            return []
        events.append(self.frameunit.ui_thread)
        return [AlertInfo(lockContentionAlertInfo,min(starts),events,"Time Spent:"+str(duration),"LockContentionAlert")]
    def getSchedulingAlert(self):
        schedulingAlertInfo="Scheduling delay', 'Work to produce this frame was descheduled for several milliseconds, contributing to jank. Ensure that code on the UI thread doesn\'t block on work being done on other threads, and that background threads (doing e.g. network or bitmap loading) are running at android.os.Process#THREAD_PRIORITY_BACKGROUND or lower so they are less likely to interrupt the UI thread. These background threads should show up with a priority number of 130 or higher in the scheduling section under the Kernel process."
        totalduration=0
        totalStats=0
        return []


