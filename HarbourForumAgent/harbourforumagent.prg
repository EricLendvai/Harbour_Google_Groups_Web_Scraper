define class HarbourForumAgent AS session OLEPUBLIC

version        = "1.2.5"
ErrorMessage   = ""
NumberOfErrors = 0
DataPath       = ""

LastForumName  = ""
LastForum_hbwgfst_key = 0

&&Used between Start/End of processing Topic Messages
p_hbwgfst_key        = 0
p_hbwgfth_key        = 0
p_hbwgfth_fstmessdt  = dtot({})
p_hbwgfth_lstmessdt  = dtot({})
p_hbwgfth_glgmessdt  = dtot({})
p_hbwgfth_curmesscnt = 0
p_hbwgfth_delmesscnt = 0

*====================================================================================================================================
procedure init
endproc
*====================================================================================================================================
function GetForumKey(par_ForumName)

local l_ForumName
local array l_SQLResult(1,1)
local l_result

l_ForumName = lower(alltrim(par_ForumName))

if this.LastForumName == l_ForumName
	l_result = this.LastForum_hbwgfst_key
else
	&&Since there is no index on the "name" field, do a case insentive search
	select hbwgfst.key;
	 from  hbwgfst;
	 where lower(trim(hbwgfst.name)) == l_ForumName;
	 and   hbwgfst.status = 1;
	 into array l_SQLResult
	if _tally = 1
		this.LastForum_hbwgfst_key = l_SQLResult[1,1]
		l_result = this.LastForum_hbwgfst_key
	else
		l_result = 0
	endif
endif

return l_result

endfunc
*====================================================================================================================================
procedure OpenData(par_Path)
&&Parameters have to be listed in the declaration above and not via "lparameter"

this.DataPath = addbs(par_Path)
this.CloseData()

use (par_Path+"hbwgfus") alias hbwgfus in 0 again shared
use (par_Path+"hbwgfst") alias hbwgfst in 0 again shared
use (par_Path+"hbwgfth") alias hbwgfth in 0 again shared
use (par_Path+"hbwgfms") alias hbwgfms in 0 again shared

endproc
*====================================================================================================================================
procedure CloseData

use in select("hbwgfus")
use in select("hbwgfst")
use in select("hbwgfth")
use in select("hbwgfms")

use in select("ListOfPreUpdateMessagesOnFile")

endproc
*====================================================================================================================================
function GetNextKey(par_tablename)
local l_key
use in select("GetLastKey")
use (dbf(par_tablename)) again alias GetLastKey in 0 order tag key
goto bottom in GetLastKey
if eof("GetLastKey")
	l_key = 1
else
	l_key = GetLastKey.key+1
endif
use in select("GetLastKey")
return l_key
endfunc
*====================================================================================================================================
function GetForumUserRecordKey(par_hbwgfst_key,par_UserName)

local l_hbwgfus_key
local l_UserName
local array l_SQLResult(1,1)

l_UserName = padr(allt(par_UserName),len(hbwgfus.name))  &&Since index exist on the "name" field, will ensure search string is padded to the same length as the field in the table. This also increases performance in VFP.

select hbwgfus.key;
 from  hbwgfus;
 where hbwgfus.name = l_UserName;
 and   hbwgfus.p_hbwgfst = par_hbwgfst_key;
 into array l_SQLResult

if empty(_tally)
	&&Add user
	l_hbwgfus_key = this.GetNextKey("hbwgfus")
	l_now         = datetime()
	insert into hbwgfus (key,;
	                     sysc,;
	                     sysm,;
	                     p_hbwgfst,;
	                     name;
	                     ) value (;
	                     l_hbwgfus_key,;
	                     l_now,;
	                     l_now,;
	                     par_hbwgfst_key,;
	                     l_UserName)
else
	l_hbwgfus_key = l_SQLResult[1,1]
endif

return l_hbwgfus_key
*====================================================================================================================================
function UpdateTopicStart(par_ForumName,par_TopicID,par_TopicSubject,par_TopicUserName,par_TopicDatetime,par_MessageCount,par_ViewCount)   &&Called at the begining of processing a topic
private all like l_*   && Crude method to avoid having to declare all variables as "local"

l_hbwgfst_key = this.GetForumKey(par_ForumName)

l_TopicID = padr(allt(par_TopicID),len(hbwgfth.ID))
l_hbwgfus_key_Topic  = this.GetForumUserRecordKey(l_hbwgfst_key,par_TopicUserName)

l_TopicDatetime = ctot(par_TopicDatetime)

this.p_hbwgfth_glgmessdt = l_TopicDatetime  && Should simply use the value reported by Google Forum, since it is buggy to start with. Will be used in the UpdateTopicEnd method if called.

l_now = datetime()

this.p_hbwgfst_key = l_hbwgfst_key

select hbwgfth.key,;
       hbwgfth.p_hbwgfus ,;
       hbwgfth.viewcnt,;
       hbwgfth.fstmessdt,;
       hbwgfth.lstmessdt,;
       hbwgfth.glgmessdt,;
       hbwgfth.delmesscnt,;
       hbwgfth.curmesscnt,;
       hbwgfth.subject;
 from  hbwgfth;
 where hbwgfth.p_hbwgfst = l_hbwgfst_key;
 and   hbwgfth.id = l_TopicID;
 into array l_SQLResult

if _tally = 1
	l_hbwgfth_key        = l_SQLResult[1,1]
	l_hbwgfth_p_hbwgfus  = l_SQLResult[1,2]
	l_hbwgfth_viewcnt    = l_SQLResult[1,3]
	l_hbwgfth_fstmessdt  = l_SQLResult[1,4]
	l_hbwgfth_lstmessdt  = l_SQLResult[1,5]
	l_hbwgfth_glgmessdt  = l_SQLResult[1,6]
	l_hbwgfth_delmesscnt = l_SQLResult[1,7]
	l_hbwgfth_curmesscnt = l_SQLResult[1,8]
	l_hbwgfth_subject    = allt(l_SQLResult[1,9])
	
	if l_hbwgfth_p_hbwgfus <> l_hbwgfus_key_Topic or ;
	   l_hbwgfth_subject   <> par_TopicSubject or ;
	   l_hbwgfth_viewcnt   <> par_ViewCount
		if seek(l_hbwgfth_key,"hbwgfth","key")
			replace hbwgfth.sysm      with l_now               in hbwgfth
			replace hbwgfth.p_hbwgfus with l_hbwgfus_key_Topic in hbwgfth
			replace hbwgfth.subject   with par_TopicSubject    in hbwgfth
			replace hbwgfth.viewcnt   with par_ViewCount       in hbwgfth
		endif
	endif
	
	if l_hbwgfth_curmesscnt = par_MessageCount and ;
	   l_hbwgfth_glgmessdt  = l_TopicDatetime and ;
	   l_hbwgfth_p_hbwgfus  = l_hbwgfus_key_Topic                 &&Number of Non Deleted Messages and Last Message Time did not change and User key.
		l_hbwgfth_key = 0
		
	else
		&&Check fields did not change
		this.p_hbwgfth_key        = l_hbwgfth_key
		this.p_hbwgfth_fstmessdt  = l_hbwgfth_fstmessdt
		this.p_hbwgfth_lstmessdt  = l_hbwgfth_lstmessdt
		this.p_hbwgfth_delmesscnt = l_hbwgfth_delmesscnt
		this.p_hbwgfth_curmesscnt = l_hbwgfth_curmesscnt
		
		&& Cursor with the list of current topic messages, to help detect deleted ones
		select hbwgfms.key,;
		       hbwgfms.deleted,;
		       hbwgfms.dati,;
		       hbwgfms.p_hbwgfus,;
		       .f. as OnFile;
		 from  hbwgfms;
		 where hbwgfms.p_hbwgfth = this.p_hbwgfth_key;
		 order by hbwgfms.dati;
		 into cursor ListOfPreUpdateMessagesOnFile readwrite
		
	endif
else
	&&Add missing Topic Record
	l_hbwgfth_key = this.GetNextKey("hbwgfth")
	l_NoDateTime  = dtot({})
	
	this.p_hbwgfth_key        = l_hbwgfth_key
	this.p_hbwgfth_fstmessdt  = l_NoDateTime
	this.p_hbwgfth_lstmessdt  = l_NoDateTime
	this.p_hbwgfth_delmesscnt = 0
	this.p_hbwgfth_curmesscnt = 0
	
	insert into hbwgfth (key,;
	                     sysc,;
	                     sysm,;
	                     p_hbwgfst,;
	                     p_hbwgfus,;
	                     id,;
	                     subject,;
	                     fstmessdt,;
	                     lstmessdt,;
	                     glgmessdt,;
	                     curmesscnt,;
	                     viewcnt;
	                     ) value (;
	                     l_hbwgfth_key,;
	                     l_now,;
	                     l_now,;
	                     l_hbwgfst_key,;
	                     l_hbwgfus_key_Topic,;
	                     trim(l_TopicID),;
	                     par_TopicSubject,;
	                     l_NoDateTime,;
	                     l_NoDateTime,;
	                     l_NoDateTime,;
	                     0,;
	                     par_ViewCount)
	
	&& Create an empty cursor
	select hbwgfms.key,;
	       hbwgfms.deleted,;
	       hbwgfms.dati,;
	       hbwgfms.p_hbwgfus,;
	       .f. as OnFile;
	 from  hbwgfms;
	 where .f.;
	 into cursor ListOfPreUpdateMessagesOnFile
	
endif

return l_hbwgfth_key   && return -1 if Topic is missing, 0 if nothing to change, the Topic key, if message count missmatch
endfunc
*====================================================================================================================================
function RecordMessage(par_MessageID,par_MessageUserName,par_MessageDatetime,par_MessageHTML)
private all like l_*   && Crude method to avoid having to declare all variables as "local"

this.ErrorMessage = ""

l_select = iif(used(),select(),0)

l_hbwgfth_key         = this.p_hbwgfth_key
l_MessageID           = allt(par_MessageID)
l_MessageDatetime     = ctot(par_MessageDatetime)
l_hbwgfus_key_Message = this.GetForumUserRecordKey(this.p_hbwgfst_key,par_MessageUserName)

if !empty(l_hbwgfth_key)
	
	&&Check Message not already on file
	if !empty(l_MessageID)
		l_MessageIDForSearch = padr(l_MessageID,len(hbwgfms.id))
		select hbwgfms.key,;
		       hbwgfms.id,;
		       hbwgfms.html;
		 from  hbwgfms;
		 where hbwgfms.p_hbwgfth = l_hbwgfth_key;
		 and   ((hbwgfms.id = l_MessageIDForSearch) or ((hbwgfms.dati = l_MessageDatetime) and (hbwgfms.p_hbwgfus = l_hbwgfus_key_Message) and empty(hbwgfms.id)));
		 into array l_SQLResult
	else
		select hbwgfms.key,;
		       hbwgfms.id,;
		       hbwgfms.html;
		 from  hbwgfms;
		 where hbwgfms.p_hbwgfth = l_hbwgfth_key;
		 and   hbwgfms.dati = l_MessageDatetime;
		 and   hbwgfms.p_hbwgfus = l_hbwgfus_key_Message;
		 into array l_SQLResult
	endif
	
	if empty(_tally)
		&&Need to append Message
		l_hbwgfms_key = this.GetNextKey("hbwgfms")
		l_now         = datetime()
		insert into hbwgfms (key,;
		                     sysc,;
		                     sysm,;
		                     p_hbwgfth,;
		                     p_hbwgfus,;
		                     id,;
		                     dati,;
		                     html;
		                     ) value (;
		                     l_hbwgfms_key,;
		                     l_now,;
		                     l_now,;
		                     l_hbwgfth_key,;
		                     l_hbwgfus_key_Message,;
		                     l_MessageID,;
		                     l_MessageDatetime,;
		                     par_MessageHTML)
	else
		l_hbwgfms_key  = l_SQLResult[1,1]
		l_hbwgfms_id   = allt(l_SQLResult[1,2])
		l_hbwgfms_html = l_SQLResult[1,3]
		
		if (l_hbwgfms_id <> l_MessageID) or (l_hbwgfms_html <> par_MessageHTML)
			if seek(l_hbwgfms_key,"hbwgfms","key")
				replace hbwgfms.id   with l_MessageID     in hbwgfms
				if hbwgfms.html <> par_MessageHTML
					replace hbwgfms.html with par_MessageHTML in hbwgfms
				endif
			endif
		endif
		
		select ListOfPreUpdateMessagesOnFile
		locate for ListOfPreUpdateMessagesOnFile->key = l_hbwgfms_key
		if found()
			replace ListOfPreUpdateMessagesOnFile->OnFile with .t.
		endif
		
	endif
	
endif

select (l_select)

return ""
endfunc
*====================================================================================================================================
function UpdateTopicEnd(par_NumberOfDeletedMessages)
private all like l_*   && Crude method to avoid having to declare all variables as "local"

l_NoDateTime = dtot({})
l_now = datetime()
l_select = iif(used(),select(),0)

&&Fix deleted flag of previously on file messages
select ListOfPreUpdateMessagesOnFile
scan all for ListOfPreUpdateMessagesOnFile->deleted = ListOfPreUpdateMessagesOnFile->OnFile
	if seek(ListOfPreUpdateMessagesOnFile->key,"hbwgfms","key")
		replace hbwgfms.sysm    with l_now                                  in hbwgfms
		replace hbwgfms.deleted with !ListOfPreUpdateMessagesOnFile->OnFile in hbwgfms
	endif
endscan

use in select("ListOfPreUpdateMessagesOnFile")

&&Fix non normalized fields fstmessdt and lstmessdt, and also field delmesscnt in hbwgfth
select hbwgfms.key,;
       hbwgfms.deleted,;
       hbwgfms.dati,;
       hbwgfms.p_hbwgfus;
 from  hbwgfms;
 where hbwgfms.p_hbwgfth = this.p_hbwgfth_key;
 and   !hbwgfms.deleted;
 order by hbwgfms.dati;
 into cursor ListOfMessagesOnFile

l_NumberOfMessages = _tally

if empty(l_NumberOfMessages)
	&&All messages of current topic are deleted. Should not be possible.
	l_hbwgfth_fstmessdt = l_NoDateTime
	l_hbwgfth_lstmessdt = l_NoDateTime
else
	goto top in ListOfMessagesOnFile
	l_hbwgfth_fstmessdt = ListOfMessagesOnFile.dati
	
	goto bottom in ListOfMessagesOnFile
	l_hbwgfth_lstmessdt = ListOfMessagesOnFile.dati
endif

&&Since there was at least the curmesscnt or glgmessdt field that was not matching, will have to update fields
   
if seek(this.p_hbwgfth_key,"hbwgfth","key")
	replace hbwgfth.sysm       with l_now                       in hbwgfth
	replace hbwgfth.curmesscnt with l_NumberOfMessages          in hbwgfth
	replace hbwgfth.fstmessdt  with l_hbwgfth_fstmessdt         in hbwgfth
	replace hbwgfth.lstmessdt  with l_hbwgfth_lstmessdt         in hbwgfth
	replace hbwgfth.glgmessdt  with this.p_hbwgfth_glgmessdt    in hbwgfth
	replace hbwgfth.delmesscnt with par_NumberOfDeletedMessages in hbwgfth
endif

use in select("ListOfMessagesOnFile")

select (l_select)

return 0
endfunc
*====================================================================================================================================
function EchoText(par_Text)
return par_Text
endfunc
*====================================================================================================================================
function Echo2Text(par_Text1,par_Text2)
return par_Text1+" - "+par_Text2
endfunc
*====================================================================================================================================
enddefine
