This project is to recommend valuable software features from users' perspective based on the public data on software markets. 

Some notes about the programs are as follows:

    1.The data scraped from the website of softPedia and the results of the evaluation are in the directory of data. In detail, the original data scraped from softPedia are in the folder of dataset_original; the data after filtering the duplicate ones and the flawed ones and filling the missing values of user ratings are in the folder of dataset_filtered.There are four columns in each data file. The first column is the software product name; the second column is the product descriptions; the third column is the product downloads; and the fourth column is the user rating. 

    2.The programs about extracting features from product descriptions are in the file of feature_extraction_by_collocation. The programs about linear regression are in the file of linear_regression. The programs about mining user oriented feature association rules are in the file of recommend. 

    3.When you run the programs, the path in the file of parameters should be first modified. The path is the complete file path of the project. The programs are writted with python 2.7. Some related packages are required. 

    4.When running the file of linear_regression, you should first specify the name of the data file which is saved in the sub-directory of dataset_filtered. please find the variable of file name in the main section of linear_regression file. Three kinds of sub-directories will be produced under the directory of data. The first is the results of the mined features. The second is the results of the coefficients of the features and the intercept in the estimated linear model. The third is the results of the features list of each product after selecting the features with positive coefficients. In the files under the third kind of directories, only the feature id is kept, which are splitted with ¡°/¡±. If you want to see the contents of the features, you can go to the file showing the mined features and find the features with the corresponding feature id. 

    5.When running the file of recommend, you should modify the directory from which the product feature lists will be read. And a set of files showing the results of recommendation evaluation will be produced and saved under the director of data. These files save the values of precision, recall and f_1 under different ratios. 

    6.The features identified manually are in the files of answer_manual_identified_features_compress and answer_manual_identified_feature_antivirus.

    7.If you have interests in such programs and there are some problems, please write the email to liuchun@henu.edu.cn.

    8.We would be grateful if you find some defects about the programs and send them to us. 

