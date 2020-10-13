all: localecompile
LNGS:=`find pretix_additional_links/locale/ -mindepth 1 -maxdepth 1 -type d -printf "-p %f "`

localecompile:
	django-admin compilemessages

localegen:
	django-admin makemessages --keep-pot -i build -i dist -i "*egg*" $(LNGS)

