# Web-Crawler
## steps to start
'''
1.	Pip install virtualenv (install virtual environments)
2.	python -m venv venv (create the venv files)
3.	now activate the virtual environment (venv/Scripts/activate)
4.	pip install scrapy
5.	test by type scrapy in terminal to check if scrapy is perfectly installed (scrapy)
6.	all set!
7.	now create your first project of scrapy ( scrapy startproject <projectName>)
8.	then go into the spider folder (using cd path/path/spider)
9.	then create genspider following with the website you want to scrape (scrapy genspider <name> <url>(in url you can remove https and www and use normal name like google.com)
10.	then, install ipython shell which can directly fetch the data(or html) and then we can test it accordingly before using it in the main code. (pip install ipython)
11.	 add a separate line to use ipython in scrapy.cfg file, under settings (shell = ipython)
12.	Then start using scrapy shell in the cmd (scrapy shell)
13.	Then start with fetch command (fetch(“full url”))

14.	for pandas (pip install pandas)
15.	with pandas you need openpyxl (pip install openpyxl)

16.	To run the spider -> go to spider folder then write in terminal (scrapy crawl <spider_name> -o <json_file_name.json> )
17.	it will create a json file and store all the data while running the crawler.
'''
