# -*- coding: utf-8 -*-
# Module: summarise.py
# About: Produce summary data of Newspaper articles and comments shared on Facebook

import json
import pandas
import os
import csv
import dateutil.parser


def summarise_article(article_file, story_name):

    with open(article_file, 'r') as json_data:
        
        article = json.load(json_data)

        if 'likes_count' not in article:
            article['likes_count'] = 0

        if 'comments_count' not in article:
            article['comments_count'] = 0

        if 'shares_count' not in article:
            article['shares_count'] = 0

        article['story_name'] = story_name

        return article


def summarise_reaction(article, reaction_file):

    reaction = pandas.read_csv(reaction_file)
    types = reaction.type.value_counts()
    
    article['reaction_like'] = types.get('LIKE') if types.get('LIKE') is not None else 0
    article['reaction_sad'] = types.get('SAD') if types.get('SAD') is not None else 0
    article['reaction_wow'] = types.get('WOW') if types.get('WOW') is not None else 0
    article['reaction_angry'] = types.get('ANGRY') if types.get('ANGRY') is not None else 0
    article['reaction_haha'] = types.get('HAHA') if types.get('HAHA') is not None else 0
    
    return article


def summarise_comment(comment_file, story_name, story_time):

    try:

        with open(comment_file, 'r') as json_data:

            comments = []

            comment_json = json.load(json_data)

            for c in comment_json:

                article_dt = dateutil.parser.parse(story_time)
                comment_dt = dateutil.parser.parse(c['created_time'])
                relative_time = (comment_dt - article_dt).total_seconds()

                comment = {}
                comment['story_name'] = story_name
                comment['created_time'] = c['created_time']
                comment['user_id'] = c['from']['id']
                comment['comment_count'] = c['comment_count']
                comment['like_count'] = c['like_count']
                comment['timedelta'] = relative_time
                comment['year'] = comment_dt.year
                comment['month'] = comment_dt.month
                comment['day'] = comment_dt.day
                comment['hour'] = comment_dt.hour
                comment['minute'] = comment_dt.minute
                comment['second'] = comment_dt.second
                comment['time_bin'] = get_time_bin(relative_time)
                comments.append(comment)

            return comments

    except FileNotFoundError:
        print('Missing story: {0}'.format(story_name)) 


def get_time_bin(relative_time):

    start = 0
    stop = 3600
    increment = 3600

    for i in range(24):
        if relative_time >= start and relative_time < stop:
            return i + 1
        else:
            start = stop
            stop += increment

    return 25


def summarise_articles(dirname, story_name):

    files = os.listdir(dirname)
    
    summaries = []
    comments = []

    for f in files:

        if '_article.json' in f:

            article_path = '{0}{1}{2}'.format(dirname, os.path.sep, f)
            reaction_path = '{0}{1}{2}_reactions.csv'.format(
                dirname, os.path.sep, f[:-len('_article.json')])

            comment_path = '{0}{1}{2}_comments.json'.format(
                dirname, os.path.sep, f[:-len('_article.json')])
            
            article = summarise_article(article_path, story_name)
            article = summarise_reaction(article, reaction_path)

            comment = summarise_comment(comment_path, 
                f[:-len('_article.json')], article['created_time'])
            
            summaries.append(article)
            if comment is not None: comments += comment

    return (summaries, comments)


def summarise_all_articles():

    story_names = [
        'A50_Commons', 
        'A50_Lords', 
        'A50_Triggered', 
        'Budget',
        'Grenfell_reactions',
        'Immigration',
        'Indyref2']

    articles = []
    comments = []

    for sn in story_names:

        dirname = 'data{0}{1}'.format(os.path.sep, sn)
        a, c = summarise_articles(dirname, sn)

        articles += a
        comments += c

    return articles, comments


def save_data(data, csv_name):

    with open(csv_name, 'w', newline='') as csv_file:
    
        writer = csv.DictWriter(csv_file, fieldnames=data[0].keys())
        writer.writeheader()
        
        for d in data:
            writer.writerow(d)

