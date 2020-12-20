inputs_info = {

    # NOTE: No flags for regex

    "fullname" : {
        "min-length": 1,
        "max-length": 1024,
        "regex": r"^([A-Za-zÀ-ÖØ-öø-ÿ']+\ )*([A-Za-zÀ-ÖØ-öø-ÿ']+)+$",
        "regex-note": "Invalid name",
    },

    "username" : {
        "min-length": 5,
        "max-length": 15,
        "regex": r"^([A-Za-z0-9._-]+)$",
        "regex-note": "Invalid username(letters, numbers, dots, underscores & dashes only)",
    },

    "email" : {
        "min-length": 5,
        "max-length": 254,
        "regex": r"^[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?\.)+[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?$",
        "regex-note": "Invalid email",
    },

    "password" : {
        "min-length": 8,
        "max-length": 256,
        "regex": r"^[^\"\'\`\\;(){}[\]<>]+",
        "regex-note": "Invalid password(no \" \' \` \\ ; ( ) { } [ ] < > allowed)",
    },

    "pypi_token" : {
        "min-length": 172,
        "max-length": 172,
        "regex": r"^pypi-[A-Za-z0-9._-]{167}$",
        "regex-note": "Invalid token",
    },

    "github_token" : {
        "min-length": 40,
        "max-length": 40,
        "regex": r"^[0-9a-f]{40}$",
        "regex-note": "Invalid token",
    },

    "pkg_name" : {
        "min-length": 3,
        "max-length": 30,
        "regex": r"^([A-Za-z0-9._-]+)$",
        "regex-note": "Invalid name(letters, numbers, dots, underscores, and dashes only)",
    },

    "github_username": {
        "min-length": 1,
        "max-length": 39,
        "regex": r"^([A-Za-z0-9]{1}[A-Za-z0-9-]{0,37}[A-Za-z0-9]?)$",
        "regex-note": "Invalid GitHub username",
    },

    "github_repo_name": {
        "min-length": 1,
        "max-length": 100,
        "regex": r"^([A-Za-z0-9.\-_]{1,100})",
        "regex-note": "Invalid GitHub repository name",
    },

    "setup_name": {
        "min-length": 1,
        "max-length": 256,
        "regex": r"^([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9._-]*[A-Za-z0-9])$",
        "regex-note": "Invalid name(letters, numbers, period, underscore, and hyphens only & start and end with a letter or number)",
    },

    "setup_version": {
        "min-length": 1,
        "max-length": 256,
        "regex": r"^([1-9][0-9]*!)?(0|[1-9][0-9]*)(\.(0|[1-9][0-9]*))*((a|b|rc)(0|[1-9][0-9]*))?(\.post(0|[1-9][0-9]*))?(\.dev(0|[1-9][0-9]*))?$",
        "regex-note": "Invalid varsion(comply with PEP440|ex. 1, 2.4, 1.5.7, etc.)",
    },

    "setup_description": {
        "min-length": 1,
        "max-length": 256,
        "regex": r"^[\"\'\`\\]{1,256}$",
        "regex-note": "Invalid description(no \" ' ` \\ allowed)",
    },

    "setup_long_description": {
        "min-length": 1,
        "max-length": 1024,
        "regex": r"^[^\"\'\`\\]{1,1024}$",
        "regex-note": "Invalid description(no \" ' ` \\ allowed)",
    },

    "setup_keywords": {
        "min-length": 1,
        "max-length": 512,
        "regex": r"^([A-Za-z0-9_]{1,64}){1}(,\ [A-Za-z0-9_]{1,64})*([A-Za-z0-9_]{1,64})?$",
        "regex-note": "Invalid keywords(letters, numbers, underscores only & seperated by comma followed by space)",
    },

    "setup_python_version": {
        "min-length": 1,
        "max-length": 1,
        "regex": r"^(2|3)$",
        "regex-note": "Invalid version(must be 2 or 3)",
    },
}


setup_args_info = [
    {
        "name": "name",
        "input_type": "text",
        "desc": "Your program's name on PyPI.org.",
        "ref": "https://packaging.python.org/guides/distributing-packages-using-setuptools/#name",
        "required": True
    },  # name

    {
        "name": "version",
        "input_type": "text",
        "desc": "The version of your program(e.g. 1, 2.4, 3.5.7, etc.)[ACCORDING TO PEP440].",
        "ref": "https://packaging.python.org/guides/distributing-packages-using-setuptools/#version",
        "required": True
    },  # version

    {
        "name": "description",
        "input_type": "text",
        "desc": "One-line summary of your project.",
        "ref": "https://packaging.python.org/guides/distributing-packages-using-setuptools/#description",
        "required": False
    },  # description

    {
        "name": "keywords",
        "input_type": "text",
        "desc": "Keywords describing your project(seperated by comma and space[keyword 1, keyword 2, keyword 3]).",
        "ref": None,
        "required": False
    },  # keywords

    {
        "name": "python_version",
        "input_type": "select",
        "select_values": [2, 3],
        "desc": "Python version your project is made for.",
        "ref": None,
        "required": True
    },  # python
    {
        "name": "long_description",
        "input_type": "area",
        "desc": "Package's long description and documentation using GitHub's Markdown.",
        "ref": "https://guides.github.com/features/mastering-markdown/",
        "required": False
    },  # long_description
]


pkg_action_queue = []
