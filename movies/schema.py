from collections import namedtuple
import json
import graphene
import requests
from graphene_django.types import DjangoObjectType
from graphene import ObjectType, String, Boolean, ID, Field, Int

from movies.models import Actor, Movie

def _json_object_hook(d):
    return namedtuple('X', d.keys())(*d.values())

def json2obj(data):
    return json.loads(data, object_hook=_json_object_hook)

class Weather(ObjectType):
    weather= String()
    visibility=Int()


class Assessmentd(ObjectType):
    compositionUid = String()

# Create a GraphQL type for the actor model
class ActorType(DjangoObjectType):
    class Meta:
        model=Actor

# Create a GraphQL type for the movie model
class MovieType(DjangoObjectType):
    class Meta:
        model=Movie

# Create a Query Type

class Query(ObjectType):
    actor=graphene.Field(ActorType, id=graphene.Int())
    movie = graphene.Field(MovieType, id=graphene.Int())
    actors=graphene.List(ActorType)
    movies = graphene.List(MovieType)
    city = graphene.Field(Weather)
    ehrAssessment = graphene.Field(Assessmentd)

    def resolve_actor(self, info, **kwargs):
        id = kwargs.get('id')

        if id is not None:
            return Actor.objects.get(pk=id)

        return None

    def resolve_movie(self, info, **kwargs):
        id = kwargs.get('id')

        if id is not None:
            return Movie.objects.get(pk=id)

        return None

    def resolve_actors(self, info, **kwargs):
        return Actor.objects.all()

    def resolve_movies(self, info, **kwargs):
        return Movie.objects.all()

    def resolve_city(self,info,**kwargs):
        url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&APPID=d7f3c8d25586e840fb2703b4858f4c59'
        city = "Sofia"
        r = requests.get(url.format(city)).json()
        print(r)
        z=json2obj(json.dumps(r))
        print(z[0])
        return z
    def resolve_ehrAssessmentd(self, info, **kwargs):
        url_read = 'https://cdr.code4health.org/rest/v1/composition/16c621db-179a-4803-9c60-8bab41e84b86::f3240965-15b7-4333-a0aa-9daa131dea16::1?format=FLAT&nhsNumber=99999990003'

        headers = {
            'Content-Type': "application/json",
            'Ehr-Session-disabled': "{{Ehr-Session}}",
            'Authorization': "Basic ZjMyNDA5NjUtMTViNy00MzMzLWEwYWEtOWRhYTEzMWRlYTE2OiQyYSQxMCQ2MTlraQ==",
            'User-Agent': "PostmanRuntime/7.15.2",
            'Accept': "*/*",
            'Cache-Control': "no-cache",
            'Postman-Token': "6cb4fa05-51e2-4028-af31-d99de241afea,85aae0a2-f395-4c9d-b08b-3e77c547bfc4",
            'Host': "cdr.code4health.org",
            'Accept-Encoding': "gzip, deflate",
            'Connection': "keep-alive",
            'cache-control': "no-cache"
        }

        r = requests.get(url_read, headers=headers).json()
        print(r["compositionUid"])

        return r



# Create Input Object Types
class ActorInput(graphene.InputObjectType):
    id = graphene.ID()
    name = graphene.String()

class MovieInput(graphene.InputObjectType):
    id = graphene.ID()
    title = graphene.String()
    actors = graphene.List(ActorInput)
    year = graphene.Int()

# Create mutations for actors
class CreateActor(graphene.Mutation):
    class Arguments:
        input = ActorInput(required=True)

    ok = graphene.Boolean()
    actor = graphene.Field(ActorType)

    @staticmethod
    def mutate(root, info, input=None):
        ok = True
        actor_instance = Actor(name=input.name)
        actor_instance.save()
        return CreateActor(ok=ok, actor=actor_instance)

class UpdateActor(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = ActorInput(required=True)

    ok = graphene.Boolean()
    actor = graphene.Field(ActorType)

    @staticmethod
    def mutate(root, info, id, input=None):
        ok = False
        actor_instance = Actor.objects.get(pk=id)
        if actor_instance:
            ok = True
            actor_instance.name = input.name
            actor_instance.save()
            return UpdateActor(ok=ok, actor=actor_instance)
        return UpdateActor(ok=ok, actor=None)

# Create mutations for movies
class CreateMovie(graphene.Mutation):
    class Arguments:
        input = MovieInput(required=True)

    ok = graphene.Boolean()
    movie = graphene.Field(MovieType)

    @staticmethod
    def mutate(root, info, input=None):
        ok = True
        actors = []
        for actor_input in input.actors:
          actor = Actor.objects.get(pk=actor_input.id)
          if actor is None:
            return CreateMovie(ok=False, movie=None)
          actors.append(actor)
        movie_instance = Movie(
          title=input.title,
          year=input.year
          )
        movie_instance.save()
        movie_instance.actors.set(actors)
        return CreateMovie(ok=ok, movie=movie_instance)


class UpdateMovie(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = MovieInput(required=True)

    ok = graphene.Boolean()
    movie = graphene.Field(MovieType)

    @staticmethod
    def mutate(root, info, id, input=None):
        ok = False
        movie_instance = Movie.objects.get(pk=id)
        if movie_instance:
            ok = True
            actors = []
            for actor_input in input.actors:
              actor = Actor.objects.get(pk=actor_input.id)
              if actor is None:
                return UpdateMovie(ok=False, movie=None)
              actors.append(actor)
            movie_instance.title=input.title
            movie_instance.year=input.year
            movie_instance.save()
            movie_instance.actors.set(actors)
            return UpdateMovie(ok=ok, movie=movie_instance)
        return UpdateMovie(ok=ok, movie=None)

class Mutation(graphene.ObjectType):
    create_actor = CreateActor.Field()
    update_actor = UpdateActor.Field()
    create_movie = CreateMovie.Field()
    update_movie = UpdateMovie.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)