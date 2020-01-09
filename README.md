## BackEND of the event extraction system

### 1.  Environment

1. Python2

2. JAVA1.8+

3. stanford NLP JAVA packages

   > The package cannot be uploaded due to copyright reasons
   >
   > More Details:https://github.com/stanfordnlp/CoreNLP

   

   1. Download
      - Download site:https://stanfordnlp.github.io/CoreNLP/download.html
        1. Main package
        2. Chinese parse package

   ![](./stanford.png)

   2. Combine two download files

      > Place the Chinese package in the home directory of the first file

   3. put the file on this directory

      ```xml
      .\PetrarchChineseServer\petrarch_chinese\.
      ```

### 2. change Database-dependent code

1. First place :

   1. file: eventLibApi.py
   2. line :24

   ```xml
   engine = create_engine("mysql+pymysql://root:12345678@127.0.0.1:3306/labserver?charset=utf8")
   ```

2. Second place

   1. file:textLibApi.py
   2. line:19

   ```xml
   engine = create_engine("mysql+pymysql://root:12345678@127.0.0.1:3306/labserver?charset=utf8")
   
   ```

3. Third place

   1. file:config.py
   2. line:5

   ```xml
   SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:12345678@127.0.0.1:3306/labserver?charset=utf8"
   
   ```

### 3. start

```xml
python main.py
```

