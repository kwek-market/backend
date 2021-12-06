import graphene
from users.auth_mutation import (
    TestToken,
    AccountNameRetrieval,
    SellerVerification,
    CompleteSellerVerification,
    UserAccountUpdate,
    UserPasswordUpdate,
    StoreUpdate,
    StoreLocationUpdate,
)

from users.auth_mutation import (
    CreateUser,
    ResendVerification,
    VerifyUser,
    LoginUser,
    VerifyToken,
    RevokeToken,
    RefreshToken,
    SendPasswordResetEmail,
    ChangePassword,
    StartSelling,
)
from market.mutation import *


class AuthMutation(graphene.ObjectType):
    pass


class Mutation(AuthMutation, graphene.ObjectType):
    create_user = CreateUser.Field()
    resend_verification = ResendVerification.Field()
    verify_user = VerifyUser.Field()
    login_user = LoginUser.Field()
    verify_token = VerifyToken.Field()
    revoke_token = RevokeToken.Field()
    send_password_reset_email = SendPasswordResetEmail.Field()
    change_password = ChangePassword.Field()
    refresh_token = RefreshToken.Field()
    test_token = TestToken.Field()
    start_selling = StartSelling.Field()
    account_name_retrieval = AccountNameRetrieval.Field()
    seller_verification = SellerVerification.Field()
    complete_seller_verification = CompleteSellerVerification.Field()
    user_account_update = UserAccountUpdate.Field()
    user_password_update = UserPasswordUpdate.Field()
    store_update = StoreUpdate.Field()
    store_location_update = StoreLocationUpdate.Field()
    add_category = AddCategory.Field()
    update_category = UpdateCategory.Field()
    delete_category = DeleteCategory.Field()
    create_product = CreateProduct.Field()
    update_product = UpdateProductMutation.Field()
    create_subscriber = CreateSubscriber.Field()
    add_to_cart = CreateCartItem.Field()
    delete_cart = DeleteCart.Field()
    delete_cart_item = DeleteCartItem.Field()
    add_to_wishlist = WishListMutation.Field()
    review = Reviews.Field()
