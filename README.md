# SHDKbot

Bot for handling answers for the "Что? Где? Когда?" games. 
Works in Russian language. Spreads love. 


## Overview 
Main functions:
1. Restructuring of the input into a question object. 
2. Questions line storing and editing.
3. Providing users with a current question, a correct answer and a comment 
to the question, as well as other contextual information. 


### Commands Available To Admin


### Commands Available To User 



#### Saving the Questions  

Admin takes all questions from https://db.chgk.info/. Basically their 
structure looks like this: 

`"Вопрос: { a question } Ответ: { an answer} [Комментарий: { a comment }] 
Источники(-и): { sources }"`

A raw text like this after it is sent to bot by admin is being split and 
saved as an object of a Question class with corresponding attributes 
(a question, an answer, a comment(optional)). One must copy a raw 
text from the site in full, i.e. with sources, lest a comment won't be 
saved even if it exists.

A structured question is then saved to a MongoDB db in a collection
named 'questions'.  

After a successful saving a confirming message is sent to a dialog with 
an admin.

Saving is available when an admin **is not** in a state of answering, 
otherwise any message of theirs is considered being an answer to a current 
question.

#### Checking Saved Questions 

To print all questions in the queue to a bot-admin dialog, use the 
`/print_all_questions` command. They'll be sent with an ObjectId _id 
(the default primary key for a MongoDB document) and 
a right answer. 


## TODO
###### A
* строки в отдельный модуль
* minimize main (?)
* aborted connection handling 
* statistics 
* ru to ua translation  

###### B
* tips
* 

###### C
* pics
* random bot reactions 

###### before commit 
* review TODO in code 
* update requirements.txt
* check config


### History 
###### not complete, for this good idea came to my bright mind too late 
> 17.02.2019 
> * config has been documented 
> * renamed buttons 

> 18.02.2019
> * rewrote distance
> * "работу с базой в миграцию -- "вот заодно и почитаешь"" is checked:
mongo does all the work itself 

> 20.02.2019 
> * moved keyboard markup to a module

> 21.02.2019
> * added @property to a CurrentQuestion class 

 > 22.02.2019 
 > * new command added: /change_question (changing by _id)
 > * added a decorator for checking privileges 