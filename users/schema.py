import graphene
from graphene_django import DjangoObjectType
from graphql_auth.schema import UserQuery, MeQuery
from graphql_auth import mutations
from django.contrib.auth import get_user_model

class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()

class CreateUser(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        password1 = graphene.String(required=True)
        password2 = graphene.String(required=True)
        full_name = graphene.String(required=True)
        email = graphene.String(required=True)

    def mutate(self, info, password1, password2, email, full_name):
        user = get_user_model()(
            username=email.split('@')[0],
            email=email,
            full_name=full_name,
        )
        if password1 == password2:
            user.set_password(password1)
            user.is_active = False
            user.save()
            return CreateUser(user=user)
        else:
            return "Couldn't Save User"

class AuthMutation(graphene.ObjectType):
    register = mutations.Register.Field()

class Mutation(AuthMutation, graphene.ObjectType):
    create_user = CreateUser.Field()


class Query(UserQuery, MeQuery, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)