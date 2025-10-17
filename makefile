# name
name = traction

docdir = ~/numlims.github.io/traction/
docmake = ~/numlims.github.io

# get the version from github tag
# delete the v from the version tag cause python build seems to strip it as well
version = $(shell git tag | sort -V | tail -1 | tr -d v)

all:
	ct tr/init.ct
	ct tr/main.ct
	ct test/test.ct

build:
	make
	python3 -m build --no-isolation

install:
	make build
	pip install "./dist/${name}-${version}-py3-none-any.whl" --no-deps --force-reinstall

.PHONY: test
test:
	make install
	pytest -s

doc:
	make
	pdoc "./tr" -o html
	ct tr/init.ct --tex --mdtotex "pandoc -f markdown -t latex" -o doc/init.tex
	ct tr/main.ct --tex --mdtotex "pandoc -f markdown -t latex" -o doc/main.tex

doc-publish:
	make doc
	cp -r html/* ${docdir}
	cd ${docmake} && make publish

doc-wrap:
	ct --tex -o doc/traction.tex

publish:
	make
	git push --tags
	gh release create "v${version}" "./dist/${name}-${version}-py3-none-any.whl"

publish-update: # if an asset was already uploaded, delete it before uploading again
	make
	# let the version tag point to the most recent commit
	git tag -f "v${version}"
	# delete tag on remote
	git push origin ":refs/tags/v${version}" 
	# re-push the tag to the remote
	git push --tags
	gh release delete-asset "v${version}" "${name}-${version}-py3-none-any.whl" -y
	gh release upload "v${version}" "./dist/${name}-${version}-py3-none-any.whl"
	# apparently the tag change rolled the release back to draft, set it to publish again
	gh release edit "v${version}" --draft=false
