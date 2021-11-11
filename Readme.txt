Dependencies

1. Install/update python package dependencies:

pip3 install --upgrade --user .

2. Clone/update pelican-themes:

git clone --recursive https://github.com/getpelican/pelican-themes pelican-themes -j 10

3. Clone/update pelican-plugins:

git clone --recursive https://github.com/getpelican/pelican-plugins pelican-plugins -j 10

Development

1. Do changes
2. Run 'make serve'
3. See how it looks like at http://localhost:8000

Publish

Run 'make publish'
