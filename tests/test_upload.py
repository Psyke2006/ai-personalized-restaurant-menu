import io
import pymupdf

def create_sample_menu_pdf() -> bytes:
    doc = pymupdf.open()
    page = doc.new_page()
    content = """
    Spice Bistro Menu
    Paneer Tikka - 280.00 - grilled cottage cheese with spices
    Peanut Satay Skewers - 320.00 - skewers with peanut sauce
    Dal Makhani - 220.00 - slow cooked creamy lentils
    Chicken Curry - 350.00 - tender chicken in curry
    """
    page.insert_text((50, 72), content)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes

def test_menu_upload_pdf_success(client):
    pdf_bytes = create_sample_menu_pdf()
    files = {
        "file": ("sample_menu.pdf", pdf_bytes, "application/pdf")
    }
    data = {
        "restaurant_name": "Spice Bistro PDF"
    }
    response = client.post("/api/v1/menu/upload", files=files, data=data)
    assert response.status_code == 200
    res = response.json()
    assert res["status"] == "extracted_and_parsed"
    assert res["menu_id"].startswith("m-")
    assert res["extracted_dishes_count"] >= 3
    assert len(res["dishes"]) >= 3
    assert res["dishes"][0]["id"].startswith("d-")

    # Verify retrieval
    get_res = client.get(f"/api/v1/menu/{res['menu_id']}")
    assert get_res.status_code == 200
    assert get_res.json()["total_dishes"] == res["extracted_dishes_count"]

def test_menu_upload_empty_file(client):
    files = {
        "file": ("empty.pdf", b"", "application/pdf")
    }
    response = client.post("/api/v1/menu/upload", files=files)
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "BAD_REQUEST"

def test_menu_upload_unsupported_type(client):
    files = {
        "file": ("menu.txt", b"Some random text", "text/plain")
    }
    response = client.post("/api/v1/menu/upload", files=files)
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "BAD_REQUEST"
