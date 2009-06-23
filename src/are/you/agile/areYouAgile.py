#!/usr/bin/env python
# encoding=utf-8

import cgi
import wsgiref.handlers

from os import path
from datetime import datetime
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import db

from are.you.agile.model.agile import AgileDegree, Question, Category, getAgileDegreeByUser

# 初期化
def initialize():
	c1 = Category("考えること")
	q1 = [Question(1, 1, "プログラマはすべてのプロダクトコードを他のプログラマ（少なくとも１名）にチェックしてもらっていますか？", "ペアプログラミング", 5, 0)
		 ,Question(1, 2, "チームメンバ全員が、使うと合意したすべてのプラクティスを一貫して厳格によく考えて適用していますか？", "ペアプログラミング、根本的原因分析、ふりかえり", 75, 0)
	     ,Question(1, 3, "チームメンバーは普段、仕事に集中して参加していますか？", "活き活きとした仕事", 5, 0)
	     ,Question(1, 4, "チームメンバーのほぼ全員がチームの目標の達成に向かって前進していると感じていますか？", "情報満載の仕事場", 4, 0)
	     ,Question(1, 5, "四半期に１回以上、何らかの問題が再発したことがありますか？", "根本的原因分析、ふりかえり", 0, 5)
	     ,Question(1, 6, "１ヶ月に少なくとも一度、チームは何らかの方法でプロセスを改善していますか？", "ふりかえり", 5, 0)]
	c1.setQuestions(q1)

	c2 = Category("協力すること")
	q2 = [Question(2, 1, "プログラマは質問の答えを得ようとするのではなく、いつも見当をつけようとしていますか？", "XPチーム", 0, 75)
		 ,Question(2, 2, "プログラマはいつも、必要だとわかっていたらすぐに（要求を出して返事を待たなくても）情報を手に入れることができますか？", "全員同席", 4, 0)
	     ,Question(2, 3, "チームメンバーはほとんどの場合、混乱することなくコミュニケーションできていますか？", "全員同席、ユビキタス言語", 4, 0)
	     ,Question(2, 4, "チームメンバーのほぼ全員がお互いを信頼していますか？", "XPチーム、全員同席", 4, 0)
	     ,Question(2, 5, "チームメンバーは普段、他のチームメンバーが何に取り組んでいるのか知っていますか？", "スタンドアップミーティング", 1, 0)
	     ,Question(2, 6, "１ヶ月に少なくとも一度、チームはステークホルダーに進捗をデモしていますか？", "イテレーションデモ、報告", 4, 0)
	     ,Question(2, 7, "１ヶ月に少なくとも一度、チームはステークホルダーに動くソフトウェアを提供していますか？", "イテレーションデモ", 1, 0)
	     ,Question(2, 8, "重要なステークホルダー全員が現在のチームの進捗に満足していますか？", "報告、イテレーションデモ、真の顧客の参加", 3, 0)
	     ,Question(2, 9, "重要なステークホルダー全員がチームの納品する能力を信頼していますか？", "信頼、報告", 3, 0)]
	c2.setQuestions(q2)

	c3 = Category("リリースすること")
	q3 = [Question(3, 1, "チームのプログラマなら誰でも、コマンド１つで簡単にソフトウェアをビルドしテストして明確な成功/失敗の結果を得ることができますか？", "10分ビルド", 25, 0)
		 ,Question(3, 2, "チームのプログラマなら誰でも、コマンド１つで簡単にテスト済みの納品可能なリリースをビルドすることができますか？", "10分ビルド", 5, 0)
	     ,Question(3, 3, "チームメンバー全員がプロジェクトに関連するすべての成果物（自動生成されるものは除く）に対してバージョン管理を行っていますか？", "バージョン管理", 25, 0)
	     ,Question(3, 4, "プログラマーはバージョン管理システムからまっさらな環境にチェックアウトするだけで、どんな開発マシンでもソフトウェアをビルドしテストすることができますか？", "バージョン管理", 25, 0)
	     ,Question(3, 5, "プログラマが最新のコードを入手すると、ほとんどいつでもビルドが成功してテストをすべてパスすると確信できますか？", "継続的インテグレーション", 5, 0)
	     ,Question(3, 6, "１日に少なくとも一度、プログラマ全員が自分の作業をコード本体にインテグレーションしていますか？", "継続的インテグレーション", 4, 0)
	     ,Question(3, 7, "インテグレーションのビルドは10分以内に完了しますか？", "10分ビルド", 4, 0)
	     ,Question(3, 8, "プログラマのほぼ全員がコードに関して感性を共有していますか？", "コーディング標準", 1, 0)
	     ,Question(3, 9, "プログラマは普段もともと誰が書いたかにかかわらず、チャンスがあればコードを改良しますか？", "コードの共同所有、リファクタリング", 4, 0)
	     ,Question(3, 10, "チームが仕事を仕上げた時点で、バグの発生は１ヶ月に５個以下になっていますか？", "バグなし", 1, 0)]
	c3.setQuestions(q3)

	c4 = Category("計画すること")
	q4 = [Question(4, 1, "チームメンバーのほぼ全員が、何を何のために作っていて、ステークホルダーは何を成功と見なすのかについて理解していますか？", "ビジョン", 25, 0)
		 ,Question(4, 2, "重要なステークホルダー全員が、チームが何を何のために作っていて、ステークホルダーが共通して何を成功だとみなしているかについて合意していますか？", "ビジョン", 25, 0)
	     ,Question(4, 3, "チームには成功を達成するための計画がありますか？", "リリース計画", 4, 0)
	     ,Question(4, 4, "チームは定期的に新しい情報を探して、その情報を使って成功するために計画を改善していますか？", "リリース計画", 2, 0)
	     ,Question(4, 5, "チームの計画づくりにはプログラマだけでなくビジネスの関係者の専門知識を取り入れていますか？また、参加したほぼ全員が計画は達成可能だということに合意していますか？", "計画ゲーム", 3, 0)
	     ,Question(4, 6, "チームの計画のほぼ全項目が、顧客中心で、結果優先で、順番に依存しないようになっていますか？", "ストーリー", 4, 0)
	     ,Question(4, 7, "チームは所定のタイムボックスの間隔（１ヶ月以上空けずに）で、進捗を計画と比較して、適宜計画を修正していますか？", "イテレーション", 4, 0)
	     ,Question(4, 8, "チームはタイムボックスの期間が始まる前に納品のコミットメントをして、ほとんどいつものコミットメント通りに納品していますか？", "イテレーション、「完全Done」、ゆとり、見積り", 4, 0)
	     ,Question(4, 9, "計画項目に「完了」マークを付けた後、例えば、バグ修正やリリースの洗練など、チームメンバーに予期せぬ追加の作業が発生することがありますか？", "「完全Done」", 0, 25)
	     ,Question(4, 10, "チームはほぼ常にそのリリースをコミットメント通りに納品していますか？", "リスク管理", 3, 0)]
	c4.setQuestions(q4)

	c5 = Category("開発すること")
	q5 = [Question(5, 1, "プログラマはほぼ常に最近書いたコードが意図した通りに動くという確信を持っていますか？", "テスト駆動開発", 25, 0)
		 ,Question(5, 2, "プログラマ全員が安心してコードを変更できますか？", "テスト駆動開発", 25, 0)
	     ,Question(5, 3, "プログラマがデバッグに10分以上かかるようなことが１週間に１回以上ありますか？", "テスト駆動開発", 0, 3)
	     ,Question(5, 4, "プログラマ全員が週を追うごとに少なくとも少しはコードがよくなっていることに同意できますか？", "リファクタリング、インクリメンタルな設計とアーキテクチャ", 25, 0)
	     ,Question(5, 5, "チームはイテレーションごとに顧客価値のあるストーリーを納品していますか？", "イテレーション、インクリメンタルな設計とアーキテクチャ", 3, 0)
	     ,Question(5, 6, "予期せぬ設計変更があると、既存のコードに対する変更が難しかったり高いコストがかかったりしますか？", "シンプルな設計", 0, 3)
	     ,Question(5, 7, "プログラマは技術的な問題に関する情報を得るために動くコードを使っていますか？", "スパイクソリューション", 1, 0)
	     ,Question(5, 8, "プログラマは最初にパフォーマンステストをせずにコードを最適化しますか？", "パフォーマンスの最適化", 0, 3)
	     ,Question(5, 9, "顧客の承認なしにプログラマは常にコードの最適化に１時間以上費やしていますか？", "パフォーマンスの最適化", 0, 3)
	     ,Question(5, 10, "オンサイト顧客はイテレーションの終わりにソフトウェアの動きに驚くようなことがめったにありませんか？", "インクリメンタルな要件", 4, 0)
	     ,Question(5, 11, "完成したストーリーのビジネスロジックに１ヶ月あたり１つ以上のバグが見つかりますか？", "顧客テスト", 0, 3)
	     ,Question(5, 12, "チームメンバーの誰かがチームが作り出すソフトウェアの品質について不安を持っていますか？", "探索的テスト、イテレーションデモ、真の顧客の参加", 0, 1)]
	c5.setQuestions(q5)

	return [c1, c2, c3, c4, c5]

# 過去のアジャイル度参照
class Past(webapp.RequestHandler):
	def post(self):
		usr = users.get_current_user()
		if not usr:
			self.response.out.write("<a href=\"%s\">Google アカウントでログインしてください。アカウントのない人は新規にアカウントを作成してください。</a>." % users.create_login_url("/past"))
		else:
			list = getAgileDegreeByUser(users.get_current_user())
			if not list:
				self.redirect("/start")
			param = {"list": list, "name": users.get_current_user().nickname()}
			self.response.out.write(template.render("past_agile_radar.html", param))

	def get(self):
		self.post()


# アジャイル度診断処理
class Agile(webapp.RequestHandler):
	def post(self):
		usr_nm = self.request.get("your_name")
		param = {"name": usr_nm}
		categories = initialize()
		for c in categories:
			for q in c.questions:
				q.answer(self.request.get(q.q_no))
			c.sumQuestionPoint()
		
		param["categories"] = categories
		usr = users.get_current_user()

		if usr:
			degree = AgileDegree(user = usr,
    						name = usr_nm,
    						time = datetime.today(),
    						p_thinking = categories[0].point,
    						p_cooperation = categories[1].point,
    						p_release = categories[2].point,
    						p_planing = categories[3].point,
    						p_development = categories[4].point)
			degree.put()
			param["message"] = '<div style="border: solid 2px blue; color: blue; font-size: small; padding: 5px;">診断結果は保存されました。</div>'

		self.response.out.write(template.render("agile_radar.html", param))
		
	def get(self):
		self.post()

# 診断スタートボタンの処理
class StartAYA(webapp.RequestHandler):
    def post(self):
    	usr = users.get_current_user()
    	name = ""
    	if usr:
    		name = usr.nickname()
    	else:
			name = self.request.get("your_name")

        param = {"categories": initialize(),
                  "name": name,
                  "login": users.create_login_url("/")}
        self.response.out.write(template.render("are_you_agile.html", param))
    
    def get(self):
        self.post()
    
# トップページを表示
class MainPage(webapp.RequestHandler):
	def get(self):
		usr = users.get_current_user()
		param = {"login": users.create_login_url("/")}
		usr_name = ""
		if usr:
			usr_name = usr.nickname()
		else:
			usr_name = "NO NAME"
		param["usr"] = usr_name
		self.response.out.write(template.render("top.html", param))

	def post(self):
		self.get()

def main():
	path = os.path.join(os.path.dirname(__file__), os.path.dirname('..'))
	path = os.path.join(path, os.path.dirname('html'))
	path = os.path.join(path, 'top.html')
	application = webapp.WSGIApplication([('/', MainPage), ('/start', StartAYA), ('/agile', Agile),
										('/past', Past)], debug=False)
	wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
	main()