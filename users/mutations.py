import graphene
from notifications.mutation import ReadNotification
from users.auth_mutation import (
    StoreBanner,
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
from bill.mutation import (
    ApplyCoupon,
    BillingAddress,
    BillingAddressDelete,
    BillingAddressUpdate,
    CancelOrder,
    CreateCoupon,
    PaymentInitiate,
    PickUpLocation,
    PaymentVerification,
    PickupLocationDelete,
    PickupLocationUpdate,
    PlaceOrder,
    TrackOrder,
    UnapplyCoupon,
    UpdateDeliverystatus,
    UpdateOrderProgress,
    PromoteProduct
)
from wallet.mutation import CreateInvoice, FundWallet, WalletTransactionSuccess, WithdrawFromWallet

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
    contact_us = ContactUs.Field()
    add_to_cart = CreateCartItem.Field()
    delete_cart = DeleteCart.Field()
    delete_cart_item = DeleteCartItem.Field()
    add_to_wishlist = WishListMutation.Field()
    review = Reviews.Field()
    billing_address = BillingAddress.Field()
    pickup_location = PickUpLocation.Field()
    payment_link = PaymentInitiate.Field()
    verify_payment = PaymentVerification.Field()
    place_order = PlaceOrder.Field()
    billing_address_update = BillingAddressUpdate.Field()
    billing_address_delete = BillingAddressDelete.Field()
    clicks_update = ProductClick.Field()
    pickup_location_update = PickupLocationUpdate.Field()
    pickup_location_delete = PickupLocationDelete.Field()
    store_banner = StoreBanner.Field()
    track_order = TrackOrder.Field()
    update_order_progress = UpdateOrderProgress.Field()
    promote_product = PromoteProduct.Field()
    update_delivery_status = UpdateDeliverystatus.Field()
    cancel_order = CancelOrder.Field()
    read_notification = ReadNotification.Field()
    create_invoice = CreateInvoice.Field()
    fund_wallet = FundWallet.Field()
    withdraw_from_wallet = WithdrawFromWallet.Field()
    wallet_transaction_success = WalletTransactionSuccess.Field()
    decrease_cart_item_quantity = DecreaseCartItemQuantity.Field()
    create_coupon = CreateCoupon.Field()
    apply_coupon = ApplyCoupon.Field()
    unapply_coupon = UnapplyCoupon.Field()