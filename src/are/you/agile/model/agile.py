# !/usr/bin/env python
# encoding=utf-8

# モデルクラス

from google.appengine.ext import db

# アジャイル度クラス
class AgileDegree(db.Model):
    user = db.UserProperty(required=True)
    name = db.StringProperty()
    p_thinking = db.IntegerProperty(required=True)
    p_cooperation = db.IntegerProperty(required=True)
    p_release = db.IntegerProperty(required=True)
    p_planing = db.IntegerProperty(required=True)
    p_development = db.IntegerProperty(required=True)
    time = db.DateTimeProperty(required=True)
    
def getAgileDegreeByUser(usr):
	result = db.GqlQuery("SELECT * FROM AgileDegree WHERE user = :1 order by time", usr).fetch(10)
	return result

class Question:
    # 初期化
    def __init__(self, i, j, question, note, yp, np):
        self.question = question
        self.note = note
        self.yp = yp
        self.np = np
        self.q_no = "question_%d_%d" % (i, j)

    # 回答に応じた得点を取得します
    def answer(self, ans):
    	self.ans = ans
        if (self.ans == "yes"):
            self.point = self.yp
        elif (self.ans == "no"):
            self.point = self.np
        else:
            self.point = 0

# カテゴリ
class Category:
    def __init__(self, category_name):
        self.category_name = category_name

    def setQuestions(self, questions):
        self.questions = questions

    def sumQuestionPoint(self):
        self.point = 0
        for q in self.questions:
            self.point += q.point
        self.comment = self.getComment()

    # 得点に応じてコメントを得る
    def getComment(self):
        if (self.point <= 75):
            return "すぐに改善が必要だ"
        elif (self.point <= 96):
            return "改善が必要だ"
        elif (self.point <= 99):
            return "できれば改善しよう"
        else:
            return "これ以上の改善すべき点はない"
