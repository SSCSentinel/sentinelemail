from setuptools import setup

setup(
    name="Sentinel Secure Email Client",
    version="0.1.0",
    description="End-to-end encrypted desktop email client",
    author="SSEC Team",
    author_email="press@wtpjournalism.org",
    py_modules=["main", "gui", "trial", "license", "config", "db", "mail", "crypto", "notify", "utils"],
    include_package_data=True,
    install_requires=[
        "PGPy>=0.5.4",           # pure-Python OpenPGP
        "python-gnupg>=0.4.7",   # GPG bridge
        "PyQt5>=5.15.0",         # GUI toolkit
        "SQLAlchemy>=1.4.0",     # ORM for MySQL
        "PyMySQL>=1.0.2",        # MySQL driver
        "APScheduler>=3.8.0",    # background jobs scheduler
        "cryptography>=3.4.7",   # license signing & HMAC
        "IMAPClient>=2.3.0",     # IMAP over TLS
        "aiosmtplib>=1.1.6",     # async SMTP with STARTTLS/auth
        "python-dateutil>=2.8.1",# robust date handling
        "plyer>=2.0.0",          # cross-platform notifications
        "nuitka>=1.6.1"          # for compiling to optimized executables
    ],
    entry_points={
        'console_scripts': [
            'sentinel = main:run',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
