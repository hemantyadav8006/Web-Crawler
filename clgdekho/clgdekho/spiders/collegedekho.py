import scrapy
import pandas as pd
from scrapy import signals
from pydispatch import dispatcher


class CollegedekhoSpider(scrapy.Spider):
    name = "collegedekho"
    allowed_domains = ["collegedekho.com"]
    start_urls = ["https://collegedekho.com/btech-colleges-in-india/"]

    scraped_data = []

    def __init__(self, *args, **kwargs):
        super(CollegedekhoSpider, self).__init__(*args, **kwargs)
        # Connects the spider_closed signal to the method that will save data
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    
    def parse(self, response):
        cards = response.css('div.collegeCardBox')
        for card in cards:
            item = {
                'Name': card.css('div.titleSection h3 a::text').get(),
                'College URL': card.css('div.titleSection h3 a::attr(href)').get(),
                'Image Link': card.css('div.listingCarousel img::attr(src)').get(),
            }

            # Follow the individual college URL to scrape additional details
            college_url = item['College URL']
            if college_url:
                next_college_page_url = 'https://www.collegedekho.com' + college_url
                # self.logger.debug(f"Following college URL: {college_url}")
                yield response.follow(next_college_page_url, callback=self.parse_college_page, meta={'item': item})

        # Handle pagination for the main college list
        next_page = response.xpath("//div[@class='pagination']/ul/li[@class='current']/following-sibling::li[1]/a")
        if next_page:
            next_page_url = next_page.attrib.get('href')
            if next_page_url:
                yield response.follow(next_page_url, callback=self.parse)

    def parse_college_page(self, response):
        # self.logger.info(f"Parsing college page: {response.url}")
        item = response.meta['item']
        item['College ID'] = response.css('meta[name="college_id"]::attr(content)').get()
        item['NIRF Rank'] = response.css('div.bannerData_bannerRank__oYcn1 span + span ::text').get()
        item['Established Year'] = response.css('div.bannerData_bannerYear__S1tIa span + span ::text').get()


        pagination_url = response.css('div.collegeDetailSubNavigation_detailSubNavContainer__uR9dG div.mobileContainerNone ul li')
        for pagination in pagination_url:
            if 'courses' in pagination.css('a::attr(href)').get():
                course_url = pagination.css('a::attr(href)').get()
                if course_url:
                    next_page_url = 'https://www.collegedekho.com' + course_url
                    # self.logger.debug(f"Following courses page URL: {next_page_url}")
                    yield response.follow(next_page_url, callback=self.parse_inside_college_URL_course, meta={'item': item})

    def parse_inside_college_URL_course(self, response):
        item = response.meta['item']
        courses = []

        rows = response.css("div.scrollTable table tr")
        for row in rows:
            course = row.css("td:nth-child(1)::text").get() or row.css("td:nth-child(1) a::text").get()
            fees = row.css("td:nth-child(2)::text").get() or row.css("td:nth-child(2) a::text").get()
            column3 = row.css("td:nth-child(3)::text").get() or row.css("td:nth-child(3) a::text").get()

            if not course or not fees or not column3:
                continue

            courses.append(f"{course}, {fees}, {column3}")

        item['Courses & Fees'] = courses
        
        pagination_url = response.css('div.collegeDetailSubNavigation_detailSubNavContainer__uR9dG div.mobileContainerNone ul li')
        for pagination in pagination_url:
            if 'scholarship' in pagination.css('a::attr(href)').get():
                course_url = pagination.css('a::attr(href)').get()
                if course_url:
                    next_page_url = 'https://www.collegedekho.com' + course_url
                    # self.logger.debug(f"Following courses page URL: {next_page_url}")
                    yield response.follow(next_page_url, callback=self.parse_inside_college_URL_scholarship, meta={'item': item})
            else:
                if 'placement' in pagination.css('a::attr(href)').get():
                    course_url = pagination.css('a::attr(href)').get()
                    if course_url:
                        next_page_url = 'https://www.collegedekho.com' + course_url
                        # self.logger.debug(f"Following courses page URL: {next_page_url}")
                        yield response.follow(next_page_url, callback=self.parse_inside_college_URL_placement, meta={'item': item})


    def parse_inside_college_URL_scholarship(self, response):
        item = response.meta['item']
        scholarships = []
        if 'scholarship' in response.url:
            cards = response.css('div.block + div') if 'Table of Contents' == response.css('div.block h2 ::text').get() else response.css('div.block')
            for card in cards:
                title = card.css('h2 ::text').get()
                details = card.css('div.collegeDetail_classRead__yd_kT span.collegeDetail_overview__Qr159 p ::text').get() or card.css('div.collegeDetail_classRead__yd_kT span.collegeDetail_overview__Qr159 ul li ::text').get()

                if not title or not details:
                    continue

                scholarships.append(f"{title} : {details}")
        else: 
            scholarships.append("Data Not Found!")

        item['Scholarship'] = scholarships
        
        pagination_url = response.css('div.collegeDetailSubNavigation_detailSubNavContainer__uR9dG div.mobileContainerNone ul li')
        for pagination in pagination_url:
            if 'placement' in pagination.css('a::attr(href)').get():
                course_url = pagination.css('a::attr(href)').get()
                if course_url:
                    next_page_url = 'https://www.collegedekho.com' + course_url
                    # self.logger.debug(f"Following courses page URL: {next_page_url}")
                    yield response.follow(next_page_url, callback=self.parse_inside_college_URL_placement, meta={'item': item})


    def parse_inside_college_URL_placement(self, response):
        item = response.meta['item']
        placement = []

        if 'placement' in response.url:
            card = response.css('div.block')
            head = card.css('div.block h2 ::text').get()
            details = card.css('div.block div.collegeDetail_classRead__yd_kT span.collegeDetail_overview__Qr159 p ::text').get()
            details1 = card.css('div.block div.collegeDetail_classRead__yd_kT span.collegeDetail_overview__Qr159 p + p::text').get()

            if not head or not details or not details1:
                pass
            placement.append(f"{head} : {details}, {details1}")
            
            rows = response.css("div.scrollTable table tr")
            for row in rows:
                particulars = row.css("td:nth-child(1)::text").get() or row.css("td:nth-child(1) a::text").get()
                detail = row.css("td:nth-child(2)::text").get() or row.css("td:nth-child(2) a::text").get()

                if not particulars or not detail:
                    continue

                placement.append(f"{particulars}, {detail}")
            
        else: 
            placement.append("Data Not Found!")
        
        item['Placement'] = placement
        
        pagination_url = response.css('div.collegeDetailSubNavigation_detailSubNavContainer__uR9dG div.mobileContainerNone ul li')
        for pagination in pagination_url:
            if 'cutoff' in pagination.css('a::attr(href)').get():
                course_url = pagination.css('a::attr(href)').get()
                if course_url:
                    next_page_url = 'https://www.collegedekho.com' + course_url
                    # self.logger.debug(f"Following courses page URL: {next_page_url}")
                    yield response.follow(next_page_url, callback=self.parse_inside_college_URL_cutoff, meta={'item': item})

    def parse_inside_college_URL_cutoff(self, response):
        item = response.meta['item']
        cutoff = []

        if 'cutoff' in response.url:
            
            cards = response.css('div.block')
            cutoff.append(cards[0].css('h2 ::text').get())

            if 'cutoff' in response.url:
                cards = response.css('div.block')
                first_card = cards[0]

                description = first_card.css("p::text").get()
                heading = first_card.css("h3::text").get()
                
                section_data = {
                    'Heading': heading,
                    'Description': description,
                    'Cutoff Table': []
                }

                rows = first_card.css("div.scrollTable table tr")
                cutoff_row = []
                for row in rows:
                    col1 = row.css("td:nth-child(1) ::text").get()
                    if row.css("td:nth-child(2) ::text").get() == 'Click Here':
                        col2 = (f"pdf_link: {row.css('td:nth-child(2) a::attr(href)').get()}")
                    else: 
                        col2 = row.css("td:nth-child(2) ::text").get()

                    col3 = row.css("td:nth-child(3) ::text").get(default="0")
                    col4 = row.css("td:nth-child(4) ::text").get(default="0")
                    col5 = row.css("td:nth-child(5) ::text").get(default="0")
                    col6 = row.css("td:nth-child(6) ::text").get(default="0")

                    
                    cutoff_row.append(f"{col1}, {col2}, {col3}, {col4}, {col5}, {col6}")
                    
                section_data['Cutoff Table'].append(cutoff_row)
                cutoff.append(section_data)

        else:
            cutoff.append("Data Not Found!")

        item['Cutoffs'] = cutoff
        
        pagination_url = response.css('div.collegeDetailSubNavigation_detailSubNavContainer__uR9dG div.mobileContainerNone ul li')
        for pagination in pagination_url:
            if 'pictures' in pagination.css('a::attr(href)').get():
                course_url = pagination.css('a::attr(href)').get()
                if course_url:
                    next_page_url = 'https://www.collegedekho.com' + course_url
                    # self.logger.debug(f"Following courses page URL: {next_page_url}")
                    yield response.follow(next_page_url, callback=self.parse_inside_college_URL_gallery, meta={'item': item})

    def parse_inside_college_URL_gallery(self, response):
        item = response.meta['item']
        gallery = []

        if 'pictures' in response.url:
            cards = response.css('div.collegeDekhoGallery_galleryContainer__MFUaq')
            head = cards.css('h2 ::text').get()
            gallery.append(f"{head}")
            rows = cards.css('div.collegeDekhoGallery_imgBox__t2uq0 div.collegeDekhoGallery_galleryImg__X2jTh')
            for row in rows:
                image_data = {
                    'Image link : ' : row.css('img::attr(src)').get()
                }
                gallery.append(f"{image_data}")
        else:
            gallery.append("No Data Found!")

        item['Images'] = gallery
        
        pagination_url = response.css('div.collegeDetailSubNavigation_detailSubNavContainer__uR9dG div.mobileContainerNone ul li')
        for pagination in pagination_url:
            if 'reviews' in pagination.css('a::attr(href)').get():
                course_url = pagination.css('a::attr(href)').get()
                if course_url:
                    next_page_url = 'https://www.collegedekho.com' + course_url
                    # self.logger.debug(f"Following courses page URL: {next_page_url}")
                    yield response.follow(next_page_url, callback=self.parse_inside_college_URL_reviews, meta={'item': item})

    def parse_inside_college_URL_reviews(self, response):
        item = response.meta['item']
        reviews = []

        if 'reviews' in response.url:
            head = response.css("div.box.block.reviewSummary_pddingTB20__otUxr h2::text").get()
            reviews.append(head)

            reviews_data = []
            
            likes_button = response.css("button.reviewSummary_likeBtn__ZPklW ::text").get()
            likes = response.css("div.reviewSummary_ulGroupBox__Y3S_a ul.reviewSummary_ulGroup___aQSV li ::text").getall()
            


            dislikes_button = response.css("button.reviewSummary_disLikeBtn__trevc ::text").get()
            dislikes = response.css("div.reviewSummary_ulGroupBox__Y3S_a:nth-of-type(2) ul.reviewSummary_ulGroup___aQSV li ::text").getall()
            
            reviews_data.append(f"{likes_button} :{likes}, {dislikes_button} : {dislikes}")

            reviews.append(reviews_data)

        else:
            reviews.append("Data Not Found!")
        
        item['Reviews'] = reviews
        self.scraped_data.append(item)
        
        yield item



    def spider_closed(self, spider):
        
        df = pd.DataFrame(self.scraped_data)

        df.to_excel("colleges_data.xlsx", index=False)
        df.to_json("colleges_data.json", index=False)
        self.log("Data saved to colleges_data.json")
        self.log("Data saved to colleges_data.xlsx")