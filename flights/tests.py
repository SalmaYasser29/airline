from django.db.models import Max
from django.test import Client, TestCase

from .models import Airport, Flight, Passenger

# Create your tests here.
class FlightTestCase(TestCase):

    def setUp(self):
        # Create airports
        a1 = Airport.objects.create(code="AAA", city="City A")
        a2 = Airport.objects.create(code="BBB", city="City B")

        # Create flights
        Flight.objects.create(origin=a1, destination=a2, duration=100)   # valid
        Flight.objects.create(origin=a1, destination=a1, duration=200)   # invalid: same origin/destination
        Flight.objects.create(origin=a1, destination=a2, duration=-100)  # invalid: negative duration

    # how many flights are departing from the airport?
    def test_departures_count(self):
        a = Airport.objects.get(code="AAA")
        self.assertEqual(a.departures.count(), 3)

    def test_arrivals_count(self):
        a = Airport.objects.get(code="AAA")
        self.assertEqual(a.arrivals.count(), 1)

    def test_valid_flight(self):
        a1 = Airport.objects.get(code="AAA")
        a2 = Airport.objects.get(code="BBB")
        f = Flight.objects.get(origin=a1, destination=a2, duration=100)
        self.assertTrue(f.is_valid_flight())

    def test_invalid_flight_destination(self):
        a1 = Airport.objects.get(code="AAA")
        f = Flight.objects.get(origin=a1, destination=a1)
        self.assertFalse(f.is_valid_flight())

    def test_invalid_flight_duration(self):
        a1 = Airport.objects.get(code="AAA")
        a2 = Airport.objects.get(code="BBB")
        f = Flight.objects.get(origin=a1, destination=a2, duration=-100)
        self.assertFalse(f.is_valid_flight())

    def test_index(self):
        c = Client()
        response = c.get("/")
        self.assertEqual(response.status_code, 200)
        # Expect 3 flights created in setUp
        self.assertEqual(response.context["flights"].count(), 3)

    def test_valid_flight_page(self):
        a1 = Airport.objects.get(code="AAA")
        a2 = Airport.objects.get(code="BBB")
        f = Flight.objects.get(origin=a1, destination=a2, duration=100)

        c = Client()
        response = c.get(f"/{f.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["flight"].id, f.id)

    def test_invalid_flight_page(self):
        # max id + 1 should not exist
        max_id = Flight.objects.all().aggregate(Max("id"))["id__max"]
        c = Client()
        response = c.get(f"/{max_id + 1}")
        self.assertEqual(response.status_code, 404)

    def test_flight_page_passengers(self):
        a1 = Airport.objects.get(code="AAA")
        a2 = Airport.objects.get(code="BBB")
        f = Flight.objects.get(origin=a1, destination=a2, duration=100)

        p = Passenger.objects.create(first_name="Alice", last_name="Smith")
        f.passengers.add(p)

        c = Client()
        response = c.get(f"/{f.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["passengers"].count(), 1)

    def test_flight_page_non_passengers(self):
        a1 = Airport.objects.get(code="AAA")
        a2 = Airport.objects.get(code="BBB")
        f = Flight.objects.get(origin=a1, destination=a2, duration=100)

        p = Passenger.objects.create(first_name="Bob", last_name="Johnson")

        c = Client()
        response = c.get(f"/{f.id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn(p, response.context["non_passengers"])
