import webapp2
import json

from google.appengine.ext import ndb
from google.appengine.api import users
from trashtalk import models


class EventHandler(webapp2.RequestHandler):

  def get(self):
    events = models.Event.query().fetch()
    self.response.write(json.dumps(events))


  def post(self):
    user_email = self.request.get('user_email')
    scf_username = self.request.get('scf_username')
    scf_password = self.request.get('scf_password')

    name = self.request.get('name')
    description = self.request.get('description')
    category = self.request.get('category')

    address_street = self.request.get('address_street')
    address_zip = self.request.get('address_zip')
    address_town = self.request.get('address_town')
    address_state = self.request.get('address_state')
    latitude = self.request.get('latitude')
    longitude = self.request.get('longitude')

    required = [user_email, scf_username, scf_password, name, category]
    if not all(required):
      raise webapp2.exc.HTTPBadRequest('missing required fields')

    has_exact_location = latitude and longitude
    has_full_address = address_state and address_street and address_zip and address_town
    if not (has_exact_location or has_full_address):
      raise webapp2.exc.HTTPBadRequest('missing exact location or full address')

    user = users.get_current_user()
    if not user:
      raise webapp2.exc.HTTPUnauthorized('no user is authenticated')

    event_creator = models.EventCreator(
      identity=user.user_id(),
      email=user.email(),
      seeclickfix_username=scf_username,
      seeclickfix_password=scf_password
    )
    address = None
    if has_full_address:
      address = models.Address(
        street=address_street, zip=address_zip, town=address_town, state=address_town
      )
    location = None
    if has_exact_location:
      location = ndb.GeoPt(latitude, longitude)
    new_event = models.Event(
      name=name, description=description, category=category, creator=event_creator,
      address=address, location=location
    )
    new_event.put()

    self.response.write('OK')  # TODO: This sends out a 200, right?