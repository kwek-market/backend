import graphene

from users.queries import Query
from users.mutations import Mutation

schema = graphene.Schema(query=Query, mutation=Mutation)
