from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from comtypes.client import CreateObject
import time
import sys
import dateutil.parser as DateTimeParser

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *

v_MaxNumberOfTopics     = 60
v_NumberOfTopicsToSkip  = 0

class ScrapeWebSite():
    p_geckodriverPath = "R:\\PythonPlayground\\ScrapeGoogleHarbourGroups\\geckodriver-v0.24.0-win64\\geckodriver.exe"

    def __init__(self):
        self.p_driver = webdriver.Firefox(executable_path=self.p_geckodriverPath)
        self.p_driver.implicitly_wait(5)
        self.p_wait = WebDriverWait(self.p_driver, 30)
        self.p_HarbourForumAgent = CreateObject("HarbourForumAgent.HarbourForumAgent")
        self.p_HarbourForumAgent.OpenData("C:\\web\\HBW\\data\\")
        
        #sys._wing_debugger.Break()
        
        print("Instantiated HarbourForumAgent COM object version: {}".format(self.p_HarbourForumAgent.version))
        
        self.p_WaitPageLoad = WebDriverWait(self.p_driver, 120, poll_frequency=1,
                                           ignored_exceptions=[NoSuchElementException,
                                                               ElementNotVisibleException,
                                                               ElementNotSelectableException])
        
        self.p_ForumURLTopics    = "Not Set"
        self.p_ForumURLMessages  = "Not Set"
        self.p_ForumName         = "Not Set"
    
    def __del__(self):
        #===== Closed Browser =====
        self.p_driver.quit()
        
    def SelectUserForum(self):
        self.p_ForumURLTopics    = "https://groups.google.com/forum/#!forum/harbour-users"
        self.p_ForumURLMessages  = "https://groups.google.com/forum/#!topic/harbour-users"
        self.p_ForumName         = "Harbour Users"
        
    def SelectDeveloperForum(self):
        self.p_ForumURLTopics   = "https://groups.google.com/forum/#!forum/harbour-devel"
        self.p_ForumURLMessages = "https://groups.google.com/forum/#!topic/harbour-devel"
        self.p_ForumName        = "Harbour Developers"
        
    def WaitForBrowserReady(self,par_MinimumWaitTime):
        #Waits par_MinimumWaitTime seconds, so the scrolling or page loading will at least start and trigger any Ajax call, then wait till the browser is ready
        time.sleep(par_MinimumWaitTime)
        try:
            self.p_wait.until(lambda driver: l_driver.execute_script('return document.readyState') == 'complete')
        except Exception as e:
            pass            
        
    def ProcessTopic(self,par_TopicCounter,par_NumberOfTopics,par_TopicID,par_Subject,par_By,par_VFPTTOCLastTopicTime,par_NumberOfMessages,par_NumberOfViews):
        
        l_TopicToDebug = 'NONE-qnIrcv8ivKU'
        
        #Determine if thread is already on file with the complete number of message. Also fix the View count if needed
        
        if par_TopicID == l_TopicToDebug:
            sys._wing_debugger.Break()
        
        l_COMResult = self.p_HarbourForumAgent.UpdateTopicStart(self.p_ForumName,
                                                                par_TopicID,
                                                                par_Subject,
                                                                par_By,
                                                                par_VFPTTOCLastTopicTime,     #Used to help detect if should even scan the message.
                                                                par_NumberOfMessages,         #Used to help detect if should even scan the message.
                                                                par_NumberOfViews)            #USed to update the View Count
        l_hbwgfth_key = l_COMResult[7]  #the return value is after the passed parameter
        #sys._wing_debugger.Break()
        
        if par_TopicID == l_TopicToDebug:
            sys._wing_debugger.Break()
            
        if l_hbwgfth_key != 0:  #0 means, thread already on file with the same number of messages.
            print("Forum = {} -- Processing Topic {} / {}. Topic Name = {} -- TopicID = {} -- By = {} -- Topic Time = {}".format(self.p_ForumName,par_TopicCounter,par_NumberOfTopics,par_Subject,par_TopicID,par_By,par_VFPTTOCLastTopicTime))
            
            l_URL = "{}/{}".format(self.p_ForumURLMessages,par_TopicID)
            
            l_URL += "%5B1-{}%5D".format(1000)   #Since the number of Posts/Messages do not include the hidden ones, will fake we should load 1000 messages for the current topics
            
            self.p_driver.get(l_URL)
            
            try:
                l_element = self.p_WaitPageLoad.until(EC.presence_of_element_located((By.ID, 'tm-tl')))
            except:
                sys._wing_debugger.Break()
                pass
            #self.WaitForBrowserReady(2)
            
            if par_TopicID == l_TopicToDebug:
                sys._wing_debugger.Break()
            
            l_ListOfDeletedMessages   = self.p_driver.find_elements_by_xpath("//span[contains(.,'This message has been deleted.')]")
            l_NumberOfDeletedMessages = len(l_ListOfDeletedMessages)
            
            l_ListOfMessages = self.p_driver.find_elements_by_xpath("//*[@id='tm-tl']/div")
            l_NumberOfMessages = len(l_ListOfMessages)
            
            print('Number of Current Messages = {} -- Number of Deleted Messages = {}'.format(l_NumberOfMessages,l_NumberOfDeletedMessages))
            
            #if par_TopicID == '9cNvEz6SuQY':
                #sys._wing_debugger.Break()
            
            if l_NumberOfMessages > 0:
                for l_Message in l_ListOfMessages:
                    
                    #Try to find the Message ID.
                    l_Elements = l_Message.find_elements_by_xpath(".//div[contains(@id,'b_action_')]")   #Search for span child of l_Message that as the exact matching class
                    if len(l_Elements) >= 1:
                        l_MessageID = l_Elements[0].get_attribute("id")
                        l_MessageID = l_MessageID[9:]  #remove first 9 characters "b_action_"
                    else:
                        l_MessageID = ""
                    
                    #Try to find the location of the Author of the message
                    l_Elements = l_Message.find_elements_by_class_name("F0XO1GC-F-a")
                    
                    if par_TopicID == l_TopicToDebug:
                        sys._wing_debugger.Break()
                        
                    if len(l_Elements) >= 1:   #Get the first 'Written By' location. Will only care about the last person who edited the message
                        l_MessageBy = l_Elements[0].text
                        #print("Message By = {}".format(l_MessageBy))
                        
                        #try to find the location of the message time.
                        l_Elements = l_Message.find_elements_by_xpath(".//span[@class='F0XO1GC-nb-Q F0XO1GC-b-Fb']")   #Search for span child of l_Message that as the exact matching class
                        
                        if par_TopicID == l_TopicToDebug:
                            sys._wing_debugger.Break()
                        
                        if len(l_Elements) == 1:
                            l_MessageTime        = l_Elements[0].get_attribute("title")
                            l_DatiMessageTime    = DateTimeParser.parse(l_MessageTime)  #Will be local time based
                            l_VFPTTOCMessageTime = l_DatiMessageTime.strftime("%m/%d/%Y %I:%M:%S %p")
                            
                            print("Message By = {} -- Time = {} -- ID = {}".format(l_MessageBy,l_VFPTTOCMessageTime,l_MessageID))
                            
                            l_MessageHTML = ""
                            
                            l_Elements = l_Message.find_elements_by_xpath(".//div[@dir='ltr']")
                            if len(l_Elements) > 0:
                                l_MessageHTML = l_Elements[0].get_attribute('innerHTML')     #It is possible multi blocks exists, but they are simply reference to other text.
                                #print("Message HTML = {}".format(l_MessageHTML))
                            else:
                                #pass   #Message was deleted probably
                                l_Elements = l_Message.find_elements_by_xpath(".//div[@class='F0XO1GC-ed-a']")   #Search for span child of l_Message that as the exact matching class
                                for l_Element in l_Elements:
                                    l_MessageHTML += l_Element.get_attribute('outerHTML')
                                
                            if len(l_MessageHTML) > 0:
                                l_COMResult = self.p_HarbourForumAgent.RecordMessage(l_MessageID,
                                                                                     l_MessageBy,
                                                                                     l_VFPTTOCMessageTime,
                                                                                     l_MessageHTML)
                            else:
                                print("failed to find HTML")
                                #sys._wing_debugger.Break()      #FOR NOT IGNORE THIS  _M_  UNTIL 
                        else:
                            print("failed to find Message Time")
                            #sys._wing_debugger.Break()
                    else:
                        pass   #Message was deleted probably
                        #print("failed to find MessageBy")
                        #sys._wing_debugger.Break()
                        
            #When there is at least 1 Message
            l_COMResult = self.p_HarbourForumAgent.UpdateTopicEnd(l_NumberOfDeletedMessages)
            
        else:
            print("Processed Forum {}, Topic {} / {}. No Change.".format(self.p_ForumName,par_TopicCounter,par_NumberOfTopics))
                    

    def RunGetAllTopics(self):
        l_driver = self.p_driver
        l_driver.get(self.p_ForumURLTopics)
        
        #l_WaitPageLoad = WebDriverWait(l_driver, 60, poll_frequency=1,
                                         #ignored_exceptions=[NoSuchElementException,
                                                             #ElementNotVisibleException,
                                                             #ElementNotSelectableException])
        #===== Get List of Topics =====
        l_NumberOfTopics = 0
        l_FetchCounter   = 0
        l_PreviousLoadingStatus = "Initial Load"
        
        while True:
            l_FetchCounter += 1
            
            try:
                l_Elements = l_driver.find_elements_by_xpath("//div[contains(@class, 'gwt-Label')][contains(.,' topics')]")
                l_ElementLoadingStatus = l_Elements[0]
                l_CurrentLoadingStatus = l_ElementLoadingStatus.get_attribute('innerHTML')
            except:
                l_CurrentLoadingStatus = ""
                print('Failed to find Loading Status text')
                break
            
            
            #try:
                #l_Element = l_driver.find_element_by_class_name('F0XO1GC-q-P')
                #l_CurrentLoadingStatus = l_Element.get_attribute('innerHTML')
            #except:
                #l_CurrentLoadingStatus = ""
            
            if (l_CurrentLoadingStatus == l_PreviousLoadingStatus):
                break
            else:
                l_PreviousLoadingStatus = l_CurrentLoadingStatus
            
            #Extract the number of topics from l_CurrentLoadingStatus
            l_Numbers = [int(s) for s in l_CurrentLoadingStatus.split() if s.isdigit()]
            if len(l_Numbers) > 0:
                l_NumberOfTopics = l_Numbers[0]
            else:
                l_NumberOfTopics = 0
            
            if l_NumberOfTopics >= v_MaxNumberOfTopics:
                break
            
            print("Loading Status = {}".format(l_CurrentLoadingStatus))
            
            l_driver.execute_script("arguments[0].innerHTML = 'waiting';", l_ElementLoadingStatus)
            
                
            #Scroll the DIV that has the list of topics. Has to be done by calling JavaScript
            l_Elements = l_driver.find_elements_by_class_name('F0XO1GC-b-F')
            if len(l_Elements) != 1:
                break
            
            for l_Element in l_Elements:
                l_driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', l_Element)                
            
            #Waits for the loading status to have the text ' of '
            try:
                #l_element = self.p_WaitPageLoad.until(EC.text_to_be_present_in_element((By.CLASS_NAME, 'F0XO1GC-q-P'), ' of '))
                l_element = self.p_WaitPageLoad.until(EC.text_to_be_present_in_element((By.XPATH, "//div[contains(@class, 'gwt-Label')][contains(.,' topics')]"), ' of '))
            except:
                #l_Elements = l_driver.find_elements_by_class_name('F0XO1GC-q-P')
                l_Elements = l_driver.find_elements_by_xpath("//div[contains(@class, 'gwt-Label')][contains(.,' topics')]")
                if len(l_Elements) == 1:
                    for l_Element in l_Elements:
                        l_CurrentLoadingStatus = l_Element.get_attribute('innerHTML')
                        if l_CurrentLoadingStatus == "waiting":
                            print("Still marked as waiting, so the scrolling failed to update the status")
                            break
                        else:
                            print("Unknow status {}.".format(l_CurrentLoadingStatus))
                            break
                else:
                    print("Failed to find status.")
                    break
            
            
        #Process the entire loaded page
        l_ListOfTopics = {}
        
        l_ListOfTopicRows = l_driver.find_elements_by_xpath("//div[contains(@id,'topic_row_')]")
        l_NumberOfTopics = len(l_ListOfTopicRows)
        
        l_TopicCounter = 0
        
        for l_TopicRows in l_ListOfTopicRows:
            l_TopicCounter += 1
            
            if l_TopicCounter > v_MaxNumberOfTopics:
                break
            
            if l_TopicCounter > v_NumberOfTopicsToSkip:
                print("Queuing Topic {} / {} in Forum {}.".format(l_TopicCounter,l_NumberOfTopics,self.p_ForumName))
                
                #Get the Topic Name and ID
                #l_Elements = l_TopicRows.find_elements_by_class_name("F0XO1GC-q-Q")
                l_Elements = l_TopicRows.find_elements_by_xpath(".//a[contains(@href,'#!topic')]")
                
                if len(l_Elements) == 1:
                    l_ElementTopicName = l_Elements[0]
                    l_TopicName = l_ElementTopicName.text
                    l_TopicHREF = l_ElementTopicName.get_attribute("href")
                    
                    l_pos = l_TopicHREF.rfind('/')
                    l_TopicID = l_TopicHREF[l_pos+1:]
                    
                    #Get the Topic Author
                    l_Elements = l_TopicRows.find_elements_by_class_name("F0XO1GC-rb-b")
                    if len(l_Elements) == 1:
                        l_ElementTopicBy = l_Elements[0]
                        l_TopicByText = l_ElementTopicBy.text[3:]
                        
                        #Get the Topic DateTime
                        l_Elements = l_TopicRows.find_elements_by_class_name("F0XO1GC-rb-g")
                        if len(l_Elements) == 1:
                            l_ElementDivLastTopicTime = l_Elements[0]
                            l_ElementSpanLastTopicTime = l_ElementDivLastTopicTime.find_element_by_xpath("span")    #_M_  Make the search above with XPATH and find the span
                            l_TextLastTopicTime    = l_ElementSpanLastTopicTime.get_attribute("title")
                            l_DatiLastTopicTime    = DateTimeParser.parse(l_TextLastTopicTime)  #Will be local time based
                            l_VFPTTOCLastTopicTime = l_DatiLastTopicTime.strftime("%m/%d/%Y %I:%M:%S %p")
                            
                            #Get the number of Views
                            l_NumberOfViewsText = ""
                            l_Elements = l_TopicRows.find_elements_by_xpath(".//span[@class='F0XO1GC-rb-r']")   #Search for span child of l_Message that as the exact matching class
                            if len(l_Elements) >= 2:
                                l_NumberOfMessagesText = l_Elements[0].text
                                l_NumberOfViewsText    = l_Elements[1].text
                                
                                l_Numbers = [int(s) for s in l_NumberOfMessagesText.split() if s.isdigit()]
                                if len(l_Numbers) > 0:
                                    l_NumberOfMessages = l_Numbers[0]
                                else:
                                    l_NumberOfMessages = 0
                                
                                l_Numbers = [int(s) for s in l_NumberOfViewsText.split() if s.isdigit()]
                                if len(l_Numbers) > 0:
                                    l_NumberOfViews = l_Numbers[0]
                                else:
                                    l_NumberOfViews = 0
                                
                                #print("Number Of Messages = {} -- Number Of Views = {}".format(l_NumberOfMessages,l_NumberOfViews))
                                
                            #Since it could be already in the list, will use try/except
                            try:
                                l_ListOfTopics[l_TopicID] = [l_TopicName, l_TopicByText, l_VFPTTOCLastTopicTime, l_NumberOfMessages, l_NumberOfViews]
                                #print('Queued Topic "{}"'.format(l_TopicName))
                            except:
                                pass
        
        #===== Process List of Topics =====
        l_TopicCounter = 0
        for l_Topic_key,l_Topic_value in l_ListOfTopics.items():
            l_TopicCounter += 1
            
            l_TopicID              = l_Topic_key
            l_TopicName            = l_Topic_value[0]
            l_TopicByText          = l_Topic_value[1]
            l_VFPTTOCLastTopicTime = l_Topic_value[2]
            l_NumberOfMessages     = l_Topic_value[3]
            l_NumberOfViews        = l_Topic_value[4]
            #sys._wing_debugger.Break()
            self.ProcessTopic(l_TopicCounter,l_NumberOfTopics,l_TopicID, l_TopicName, l_TopicByText, l_VFPTTOCLastTopicTime, l_NumberOfMessages, l_NumberOfViews)
            
        print("Done. Detected {} topics.".format(l_NumberOfTopics))
        
    def TestCOM(self):
        l_DataLayer = CreateObject("HarbourForumAgent.HarbourForumAgent")
        print(l_DataLayer.version)
        #help(l_DataLayer)
        l_Result = l_DataLayer.EchoText("Test 002")
        l_Result = l_DataLayer.Echo2Text("Hello","World")
        print(l_Result[0])
        print(l_Result[1])
        print(l_Result[2])

if __name__ == "__main__":
    l_Scraper = ScrapeWebSite()
    l_Scraper.SelectUserForum()
    l_Scraper.RunGetAllTopics()
    del l_Scraper
    
    l_Scraper = ScrapeWebSite()
    l_Scraper.SelectDeveloperForum()
    l_Scraper.RunGetAllTopics()
    del l_Scraper

    