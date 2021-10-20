import graphene
from graphene_django import DjangoObjectType
from .models import Books


class BookType(DjangoObjectType):
    class Meta:
        model = Books
        fields = ("id", "title", "excerpt")

class Query(graphene.ObjectType):
    all_books = graphene.Field(BookType, id=graphene.Int())
    def resolve_all_books(root, info, id):
        return Books.objects.get(pk=id)

class AddBook(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        excerpt = graphene.String(required=True)
    book = graphene.Field(BookType)

    @classmethod
    def mutate(cls, root, info, title, excerpt):
        book = Books(title=title, excerpt = excerpt)
        book.save()
        return AddBook(book=book)

class UpdateBook(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        title = graphene.String(required=True)
        excerpt = graphene.String(required=True)
    book = graphene.Field(BookType)

    @classmethod
    def mutate(cls, root, info, id, title, excerpt):
        book = Books.objects.get(pk=id)
        book.title = title
        book.excerpt = excerpt
        book.save()
        return AddBook(book=book)

class DeleteBook(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
    book = graphene.Field(BookType)

    @classmethod
    def mutate(cls, root, info, id):
        book = Books.objects.get(pk=id)
        book.delete()
        return "Book {} deleted successfully".format(id)

class Mutation(graphene.ObjectType):
    add_books = AddBook.Field()
    update_books = UpdateBook.Field()
    delete_books = DeleteBook.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)