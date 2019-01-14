import csv
from optparse import make_option
import re
from django.core.management.base import BaseCommand
from knowledgebase.models import Article, TelephoneNumber, ArticleCategory, ArticleCategoryMatrix


regex = re.compile(r"\(([^,]*)\)")


class Command(BaseCommand):

    option_list = BaseCommand.option_list + (make_option("-f", "--file", dest="file", help="path to .csv file"),)

    help = "Create model objects from csv file (-f file_path)"

    required_args = ("csv", "model")

    def handle(self, *args, **options):
        if options["file"] is None:
            raise ValueError("Missing parameter. Try --help")

        self.stderr.write("Loading Articless from %s" % options["file"])

        with open(options["file"], "rU") as f:
            reader = csv.DictReader(f)
            for row in reader:
                article = Article.objects.get(pk=row["id"])
                for field_name, value in row.iteritems():
                    value = value.strip().decode("ascii", "ignore")
                    try:
                        getattr(self, "set_%s" % field_name)(article, value)
                    except AttributeError:
                        setattr(article, field_name, value)
                article.save()

    def set_helpline(self, obj, value):
        for n in value.split("\n"):
            name = ", ".join(regex.findall(n)).strip()
            number = re.sub(regex, "", n).strip()
            if number:
                t, created = TelephoneNumber.objects.get_or_create(article=obj, name=name, number=number)

    def set_categories(self, obj, value):
        for cn in value.split(","):
            try:
                cn = cn.strip().capitalize()
                ac = ArticleCategory.objects.get(name=cn)
            except ArticleCategory.DoesNotExist:
                self.stderr.write("Category %s does not exist" % cn)
                continue
            acm, created = ArticleCategoryMatrix.objects.get_or_create(article=obj, article_category=ac)
