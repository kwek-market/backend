def test_create_product_charge_success(authenticate_admin):
    query = """
    mutation CreateProductCharges($token: String!, $hasFixedAmount: Boolean!, $charge: Float!) {
        createProductCharges(token: $token, hasFixedAmount: $hasFixedAmount, charge: $charge) {
            status
            message
            productCharge {
                id
                charge
            }
        }
    }
    """
    variables = {"token": authenticate_admin, "hasFixedAmount": True, "charge": 50.00}

    client = Client(schema)
    response = client.execute(query, variables=variables)

    assert response["data"]["createProductCharges"]["status"] is True
    assert (
        response["data"]["createProductCharges"]["message"]
        == "Successfully created product charges"
    )
    assert response["data"]["createProductCharges"]["productCharge"]["charge"] == 50.00


def test_create_product_charge_already_exists(authenticate_admin):
    query = """
    mutation CreateProductCharges($token: String!, $hasFixedAmount: Boolean!, $charge: Float!) {
        createProductCharges(token: $token, hasFixedAmount: $hasFixedAmount, charge: $charge) {
            status
            message
        }
    }
    """
    variables = {"token": authenticate_admin, "hasFixedAmount": False, "charge": 100.00}

    client = Client(schema)
    response = client.execute(query, variables=variables)

    # Assuming a charge already exists
    assert response["data"]["createProductCharges"]["status"] is False
    assert (
        response["data"]["createProductCharges"]["message"]
        == "Already created a charge, you can only update!!!"
    )


def test_update_product_charge_success(authenticate_admin):
    # Assume the product charge already exists
    query = """
    mutation UpdateProductCharges($token: String!, $id: String!, $charge: Float!, $hasFixedAmount: Boolean!) {
        updateProductCharges(token: $token, id: $id, charge: $charge, hasFixedAmount: $hasFixedAmount) {
            status
            message
            productCharge {
                charge
                hasFixedAmount
            }
        }
    }
    """
    # Set valid charge ID
    product_charge_id = "some_existing_charge_id"

    variables = {
        "token": authenticate_admin,
        "id": product_charge_id,
        "charge": 75.00,
        "hasFixedAmount": False,
    }

    client = Client(schema)
    response = client.execute(query, variables=variables)

    assert response["data"]["updateProductCharges"]["status"] is True
    assert (
        response["data"]["updateProductCharges"]["message"] == "successfully updated!"
    )
    assert response["data"]["updateProductCharges"]["productCharge"]["charge"] == 75.00
