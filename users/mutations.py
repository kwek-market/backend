import graphene
from notifications.mutation import ReadNotification
from users.auth_mutation import (
    FlagVendor,
    SendEmailToUsers,
    StoreBanner,
    AccountNameRetrieval,
    SellerVerification,
    CompleteSellerVerification,
    RejectSellerVerification,
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
    UpdateOrderProgress
)
from wallet.mutation import (CreateInvoice,
FundWallet, WalletTransactionSuccess,
WithdrawFromWallet, RefundRequest,
ForceRefund)

class AuthMutation(graphene.ObjectType):
    pass


class Mutation(AuthMutation, graphene.ObjectType):
    account_name_retrieval = AccountNameRetrieval.Field()
    add_category = AddCategory.Field()
    add_to_cart = CreateCartItem.Field()
    add_to_wishlist = WishListMutation.Field()
    apply_coupon = ApplyCoupon.Field()
    billing_address = BillingAddress.Field()
    billing_address_update = BillingAddressUpdate.Field()
    billing_address_delete = BillingAddressDelete.Field()
    cancel_order = CancelOrder.Field()
    cancel_product_promotion = CancelProductPromotion.Field()
    change_password = ChangePassword.Field()
    clicks_update = ProductClick.Field()
    complete_seller_verification = CompleteSellerVerification.Field()
    reject_seller_verification = RejectSellerVerification.Field()
    flag_vendor = FlagVendor.Field()
    contact_us = ContactUs.Field()
    create_user = CreateUser.Field()
    create_product = CreateProduct.Field()
    create_subscriber = CreateSubscriber.Field()
    new_flash_sales = FlashSalesMutation.Field()
    create_invoice = CreateInvoice.Field()
    create_coupon = CreateCoupon.Field()
    delete_category = DeleteCategory.Field()
    delete_cart = DeleteCart.Field()
    delete_cart_item = DeleteCartItem.Field()
    decrease_cart_item_quantity = DecreaseCartItemQuantity.Field()
    fund_wallet = FundWallet.Field()
    login_user = LoginUser.Field()
    payment_link = PaymentInitiate.Field()
    pickup_location = PickUpLocation.Field()
    pickup_location_update = PickupLocationUpdate.Field()
    pickup_location_delete = PickupLocationDelete.Field()
    place_order = PlaceOrder.Field()
    promote_product = PromoteProduct.Field()
    read_notification = ReadNotification.Field()
    refresh_token = RefreshToken.Field()
    resend_verification = ResendVerification.Field()
    revoke_token = RevokeToken.Field()
    review = Reviews.Field()
    seller_verification = SellerVerification.Field()
    send_password_reset_email = SendPasswordResetEmail.Field()
    start_selling = StartSelling.Field()
    store_update = StoreUpdate.Field()
    store_location_update = StoreLocationUpdate.Field()
    store_banner = StoreBanner.Field()
    track_order = TrackOrder.Field()
    unapply_coupon = UnapplyCoupon.Field()
    update_category = UpdateCategory.Field()
    update_product = UpdateProductMutation.Field()
    update_order_progress = UpdateOrderProgress.Field()
    update_delivery_status = UpdateDeliverystatus.Field()
    user_account_update = UserAccountUpdate.Field()
    user_password_update = UserPasswordUpdate.Field()
    verify_user = VerifyUser.Field()
    verify_token = VerifyToken.Field()
    verify_payment = PaymentVerification.Field()
    wallet_transaction_success = WalletTransactionSuccess.Field()
    refund = RefundRequest.Field()
    force_refund = ForceRefund.Field()
    withdraw_from_wallet = WithdrawFromWallet.Field()
    send_email_to_users = SendEmailToUsers.Field()
    