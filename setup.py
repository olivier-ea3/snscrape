import setuptools


setuptools.setup(
	name = 'snscrape',
	description = 'A social networking service scraper',
	author = 'JustAnotherArchivist',
	url = 'https://github.com/JustAnotherArchivist/snscrape',
	classifiers = [
		'Development Status :: 4 - Beta',
		'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
		'Programming Language :: Python :: 3.8',
		'Programming Language :: Python :: 3.9',
	],
	packages = ['snscrape', 'snscrape.modules'],
	setup_requires = ['setuptools_scm'],
	use_scm_version = True,
	install_requires = [
		'requests[socks]',
		'torpy[requests]',
		'lxml',
		'beautifulsoup4',
		'pytz; python_version < "3.9.0"',
	],
	python_requires = '~=3.8',
	extras_require = {
		'test': ['coverage'],
		'dev': ['flake8', 'isort', 'black', 'mypy']
	},
	entry_points = {
		'console_scripts': [
			'snscrape = snscrape._cli:main',
		],
	},
)
