from lxml import etree as ET
from subprocess import call


def process_news():
    root = ET.parse("results/news.xml")
    print("Count of images for pages:")
    for page in ET.XPath("//data/page")(root):
        print("(", ET.XPath("@url")(page)[0], ") : ",
              int(ET.XPath("count(fragment[@type=\"image\"])")(page)),
              "images")


def process_bikes():
    dom = ET.parse("results/bikes.xml")
    xslt = ET.parse("xslscripts/bikes.xsl")
    transform = ET.XSLT(xslt)
    result = transform(dom)
    result.write_output("results/bikes.html")


def print_menu():
    print(30 * "-", "MENU", 30 * "-")
    print("1. Scrapy News")
    print("2. Scrapy Bikes")
    print("3. Process News")
    print("4. Process Bikes")
    print("5. Exit")
    print(67 * "-")


loop = True

while loop:  ## While loop which will keep going until loop = False
    print_menu()  ## Displays menu
    choice = int(input("Enter your choice [1-5]: "))
    if choice == 1:
        call("scrapy crawl news".split())
    elif choice == 2:
        call("scrapy crawl bikes".split())
    elif choice == 3:
        process_news()
    elif choice == 4:
        process_bikes()
    elif choice == 5:
        loop = False  # This will make the while loop to end as not value of loop is set to False
    else:
        # Any integer inputs other than values 1-5 we print an error message
        print("Wrong option selection. Enter any key to try again..")
