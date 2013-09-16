'''
Created on Jan 28, 2011

@author: yangwookkang
'''
from movie import Movie
from sqlobject import *
import sys
from sqlobject.sqlbuilder import ISNULL, ISNOTNULL, AND, OR, IN, CONTAINSSTRING
from localdb_wrapper import LocalDBWrapper
import random
from types import UnicodeType
import imdb

class IMDBWrapper:
    
    

    """
    (person,Robert Dinero)(type,movieTitle)
    (person,Inception)
    (movieTitle,Inception)(type,plot)
    (type,movieTitle)
    (type,movieTitle)
    (type,movieTitle)
    (person,Inception)(type,director)
    (type,actor)
    (type,movieTitle)
    
    (type,plot)(movieTitle,Ocean 's 11)
    (person,Steven Segal)(type,movieTitle)
    (movieTitle,Ocean 's 11)(type,director)
    (person,Michael Bay)(type,movieTitle)
    (person,Meet The Parents)(type,plot)
    (person,iRobot)
    (movieTitle,Twilight)(type,director)
    
    Person, return type, 
    """
    def __init__(self):
        ## connect to the database
        #self.db = imdb.IMDb('sql', uri='mysql://maw_imdb_team_2:XJYULPEM@mysql.cse.ucsc.edu/maw_imdb')
        self.db = imdb.IMDb()
        self.genrelist = {'short':'0','adventure':'1','drama':'2','music':'3','sci-fi':'4','action':'5','fantasy':'6','horror':'7','biography':'8','comedy':'9','musical':'10','documentary':'11','animation':'12','crime':'13','mystery':'14','romance':'15','history':'16','war':'17','western':'18','family':'19','sport':'20','News':'21','reality-tv':'22','film-Noir':'23','talk-show':'24','game-show':'25'}
        
        #movies = db.search_movie("the lord of the ring")
        self.conn = self.setConnection('mysql://maw_imdb_team_2:XJYULPEM@mysql.cse.ucsc.edu/maw_imdb').getConnection()
        #self.conn = self.setConnection('mysql://maw_imdb_team_2:XJYULPEM@127.0.0.1:9000/maw_imdb').getConnection()
        #for movie in movies:
        #    print movie.summary()
        pass
        
    def escape(self, name):
        name = name.replace(" '", "'")
        return name.replace("'", "\\'")
    
    def get_top250(self):
        return self.db.get_top250_movies()
    def get_bottom100(self):
        return self.db.get_bottom100_movies()

    def get_plot(self, title):
        plot = ""
        title = self.escape(title)
        cursor = self.conn.cursor ()
        cursor.execute ("select title, info from movie_info i, title t where t.kind_id = 1 and i.movie_id = t.id and i.info_type_id = 195 and t.title like '%{title:s}%' limit 1".format(title=title))
        rows = cursor.fetchall ()
        for row in rows:
                plot = row[1]
                break;

        cursor.close()

        return plot
    
    def get_castlist(self, title):
        cast = []
        title = self.escape(title)
        sql = "select DISTINCT n.name from cast_info c, name n where n.id = c.person_id and c.movie_id = (select id from title where kind_id = 1 and title like '%{title:s}%' limit 1) and role_id in (1,3)".format(title=title)
        cursor = self.conn.cursor ()
        cursor.execute (sql)
        rows = cursor.fetchall ()
        for row in rows:
                cast.append(self.tounicode(row[0]))
        cursor.close()

        return cast
    
    
    def encodeName(self, name):
        name = name.strip()
        comma = name.find(",")
        space = name.find(" ")
        
        if comma != -1:
            firstname = name[comma+1:].strip()
            lastname  = name[:comma].strip()
        elif space != -1:
            firstname = name[:space].strip()
            lastname  = name[space+1:].strip()
        else:
            return "'" + name + "'"
        
        return "'" + self.escape(lastname) + ", " + self.escape(firstname) + "'"
        
    
    def find_searchCriteria(self, entities):
        people = []
        year = []
        directors = []
        genres = []
        people_str = ""
        year_str = ""
        director_str =""
        genre_str = ""
        for k, v in entities.get_entityitems():
            if k == "person":
                people.append(self.encodeName(v))
            elif k == "timespan":
                index = v.find("s")
                if index == -1:
                    year.append(v)
                else:
                    period = v[:index]
                    if len(period) == 2: # 70s or 80s
                        period = "19" + period
                    
                    if len(period) == 4: # 1990s or 2000s
                        startyear = int(period)
                        for i in range(0, 10):
                            year.append(str(startyear + i))
                        
            elif k == "director":
                directors.append(self.encodeName(v))
                
            elif k == "genre":
                genres.append("'"+v+"'")
        
        if len(people) != 0:
            people_str = ",".join(people)
            people_str = "(" + people_str + ")"
        if len(year) != 0:
            year_str = ",".join(year)
            year_str = "(" + year_str + ")"
        
        if len(directors) != 0:
            director_str = "(" + ",".join(directors) + ")" 
        
        if len(genres) != 0:
            genre_str = "(" + ",".join(genres) + ")"
        
        return people_str, year_str, director_str, genre_str
    
    
    def is_person_in_movie(self, person, title):
        count = 0
        title = self.escape(title)
        name = self.encodeName(person)
        sql = "select count(*) from cast_info c, name n where n.name = {name:s} and n.id = c.person_id and c.movie_id = (select id from title where kind_id = 1 and title like '%{title:s}%' limit 1)".format(title=title, name=name)
        
        cursor = self.conn.cursor ()
        cursor.execute (sql)
        rows = cursor.fetchall ()
        if len(rows) != 0:
            count = rows[0][0]
        
        cursor.close()
        return (count > 0)
        
    
    def get_director(self, title):
        director = ""
        title = self.escape(title)
        sql = "select n.name from cast_info c, name n where n.id = c.person_id and c.movie_id = (select id from title where kind_id = 1 and title like '%{title:s}%' limit 1) and role_id = 15".format(title=title)
        
        cursor = self.conn.cursor ()
        cursor.execute (sql)
        rows = cursor.fetchall ()
        if len(rows) != 0:
            director = rows[0][0]
        
        cursor.close()
        return director
    """
    create table movie_score (
      movie_id INT,
      rate FLOAT,
      score FLOAT
    );

    """
    def rate_to_score(self, rating, unit):
        score = (float(rating) -3) * float(unit)
        if rating <= 2:
            return score * -1
        else:
            return score
    
    def update_score(self, movielist, movie_id, score):
        if movielist.has_key(movie_id):
            movielist[movie_id] = movielist[movie_id] + score
        else:
            movielist[movie_id] = score

    def tounicode(self, s):
        """Nicely print a string to sys.stdout."""
        if not isinstance(s, UnicodeType):
            s = unicode(s, 'utf_8')
        s = s.encode(sys.stdout.encoding or 'utf_8', 'replace')
        return s
    
    # rating (1 hate, 2, 3 neutral, 4, 5 like)
    # score  ( -2,  -1, 0,  1,  2)
    
    # search only movies released in 2000s
    def get_recommendation_2000s(self, entities, userpref):
        if not entities.has_entity("timespan"):
            entities.add_entity("timespan", "2000s")
            
        return self.get_recommendation(entities, userpref)
    
    # do random sort
    def get_recommendation_randomlist(self, entities, userpref):
        return self.get_recommendation(entities, userpref, True)
    
    # pick one movie randomly
    def get_recommendation_onerandom(self, entities, userpref):
        movies = self.get_recommendation(entities, userpref, False)
        random_movie = random.randrange(0, len(movies), 1)
        return movies[random_movie]

    # pick the movie that has the best score 
    def get_recommendation_onebest(self, entities, userpref):
        movies = self.get_recommendation(entities, userpref, False)
        return movies[0]    
    
    # default recommendation routine
    def get_recommendation(self, entities, userpref, doshuffle = False):
        movielist = {}
        orderbyscore = "yes"
        # no preference
        
        w1 = float(userpref["w1"])
        w2 = float(userpref["w2"])
        w3 = float(userpref["w3"])
        #print w1, w2, w3
        if len(userpref) == 0:
            orderbyscore = ""
        else:
            sql = "update yarb_score set score = 0"
            cursor = self.conn.cursor ()
            cursor.execute (sql)
            cursor.close()   
            score = 0.0
            # 1. userpref
            for key, value in userpref.iteritems():
                if 	key in ("w1", "w2", "w3", "output"):
                    continue
                if value.startswith("movie"):
                #    1.1 movie    - extract directors, actors actress -> -0.6, -0.3, 0, +0.3, +0.6
                    movietitle = self.escape(key)
                    score      = self.rate_to_score(value[len(value)-1], 0.5)
                    #print movietitle
                    personids = ""
                    sql = "select distinct GROUP_CONCAT(person_id) from cast_info c where c.movie_id = (select id from title where title like '%{title}%' and kind_id = 1 limit 1) and role_id in (1,3) limit 50".format(title=movietitle)
                    
                    cursor = self.conn.cursor ()
                    cursor.execute (sql)
                    rows = cursor.fetchall ()
                    
                    for row in rows:
                        personids = row[0]
                    
                    if personids is not None and len(personids) > 0:
                        personids = "(" + personids + ")"
                        sql = "select distinct movie_id from cast_info where person_id in " + personids + " limit 250"
                        cursor.execute(sql)
                        rows = cursor.fetchall ()
                        #print sql
                        for row in rows:
                            movie_id = row[0]                        
                            self.update_score(movielist, movie_id, score)
    
                    cursor.close()
                elif value.startswith("genre"):
                #    1.3 genre    - directly update the table  0.6
                    genre = self.escape(key)
                    score = self.rate_to_score(value[len(value)-1], 0.7)
                    genre_id = -1
                    
                    if self.genrelist.has_key(genre):
                        genre_id = self.genrelist[genre]
                    
                    if genre_id != -1:        
                        sql = "update yarb_score set score = score + (" + str(score) + ") where genre_id = " + genre_id
                        cursor = self.conn.cursor ()
                        cursor.execute (sql)
                        cursor.close()
    
                elif value.startswith("director"):
                #    1.4 director -  0.6
    
                    score      = self.rate_to_score(value[len(value)-1], 1)
                    name       = self.encodeName(key)
                    sql = "select distinct movie_id from cast_info c, name n where c.person_id = n.id and n.name = {name:s} and role_id = 15".format(name = name)
                    
                    cursor = self.conn.cursor ()
                    cursor.execute (sql)
                    rows = cursor.fetchall ()
                    for row in rows:
                        movie_id = row[0]
                        self.update_score(movielist, movie_id, score)
                    cursor.close()
                                   
                elif value.startswith("person"):
                #    1.2 person   -  0.6
                    score      = self.rate_to_score(value[len(value)-1], 1)
                    name       = self.encodeName(key)
                    sql = "select distinct movie_id from cast_info c, name n where c.person_id = n.id and n.name = {name:s}".format(name = name)
                    #print sql
                    cursor = self.conn.cursor ()
                    cursor.execute (sql)
                    rows = cursor.fetchall ()
                    for row in rows:
                        movie_id = row[0]
                        self.update_score(movielist, movie_id, score)
                    cursor.close()
              
            # 2. update movie_score table = rating + extra score 
            cursor = self.conn.cursor ()
            score = score * w3
            
            if score != 0.0:
                for movie_id, score in movielist.iteritems():
                    sql = "update yarb_score set score = score + ({score}) where movie_id = {movie_id}".format(score = score, movie_id=movie_id)
                    cursor.execute (sql)
        
            cursor.close()
        # 3. select movie names, results
        return self.get_movielist(entities, orderbyscore, doshuffle, w1, w2)
    
    def get_movielist(self, entities, orderbyscore = "", doshuffle = False, w1 = 0.3, w2 = 1.0):
        person_id_str = ""
        movie_id_str = ""
        director_id_str = ""
        genre_str = ""
        people, year_str, director, genre = self.find_searchCriteria(entities)
        movies = []
        movie_ids = []
        ## Subquery performance of the MySQL database server we're using is horrible, 
        ## so we split it into several queries
        if len(people) != 0:
        
            sql = "select distinct GROUP_CONCAT(id) from name where name in " + people
            cursor = self.conn.cursor ()
            cursor.execute (sql)
            rows = cursor.fetchall ()
            if len(rows) == 0 or rows[0][0] is None:
                cursor.close()
                return []
            
            person_id_str = "("  + rows[0][0] + ")"
            
            sql2 = "select distinct movie_id from cast_info where person_id in " + person_id_str + " and role_id in (1,3, 7, 15)";
            
            cursor.execute (sql2)
            rows = cursor.fetchall ()
            
            for row in rows:
                movie_ids.append(str(row[0]))
                
            #movie_id_str = "movie_id in (" + ",".join(movie_ids) + ")"
        
            cursor.close()

        
            
        if len(director) != 0:
            
            sql = "select distinct GROUP_CONCAT(id) from name where name in " + director
            cursor = self.conn.cursor ()
            cursor.execute (sql)
            rows = cursor.fetchall ()
            if len(rows) == 0 or rows[0][0] is None:
                cursor.close()
                return []

            director_id_str = "("  + rows[0][0] + ")"
            
            sql2 = "select distinct movie_id from cast_info where person_id in " + director_id_str + " and role_id = 15";
            
            cursor.execute (sql2)
            rows = cursor.fetchall ()
            for row in rows:
                movie_ids.append(str(row[0]))
                
            #movie_id_str = "movie_id in (" + ",".join(movie_ids) + ")"
        
            cursor.close()

        if len(genre) != 0:
            sql = "select distinct movie_id from movie_info where info_type_id = 5 and info in {genre:s}".format(genre=genre)
            cursor = self.conn.cursor ()
            cursor.execute (sql)
            rows = cursor.fetchall ()
            for row in rows:
                movie_ids.append(str(row[0]))

            cursor.close()

        movie_id_str = "s.movie_id in (" + ",".join(movie_ids) + ")"
        
        sql = "select title, production_year, (s.rating * " + str(w1) + ") + (s.score *"+ str(w2) +") + s.norm_popularity as totalscore from title t, (select distinct movie_id, rating, score, norm_popularity from yarb_score) s   where t.kind_id = 1 and s.movie_id = t.id "
        
        if len(movie_ids) != 0:
            sql += " and " + movie_id_str
        
        if year_str != "":
            sql += " and production_year in " + year_str
    
        if not doshuffle:
            if orderbyscore == "":
                sql += " order by production_year desc limit 200"
            else:
                sql += " order by totalscore desc, production_year desc limit 200"
        else:
            sql += " order by totalscore desc, production_year desc limit 200"
            
        #print sql
        cursor = self.conn.cursor ()
        cursor.execute (sql)
        rows = cursor.fetchall ()
        
        for row in rows:
            movies.append(Movie(self.tounicode(row[0]), row[1], row[2]))

        if doshuffle:
            random.shuffle(movies)

        cursor.close()
        return movies
    
    
    def setConnection(self, uri, encoding='utf8', debug=False):
        kw = {}
        _uriLower = uri.lower()
        if _uriLower.startswith('mysql'):
            kw['use_unicode'] = 1
            #kw['sqlobject_encoding'] = encoding
            kw['charset'] = encoding
        conn = connectionForURI(uri, **kw)
        conn.debug = debug
        conn.paramstyle = conn.module.paramstyle
        return conn
    
