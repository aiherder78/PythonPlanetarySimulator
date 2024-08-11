#This is a very simple 2D planetarium simulator for our solar system.
#The planet orbits are probably calculating correctly, but look circular because of the limited size.
#It uses real physics gravity dynamics and takes other planetary bodies' tugs into consideration on each update,
#though the sun makes up most of the pull.
#See the comments for neat links about the planets.

#I got inspiration (and copied mostly, then started adding planets and making modifications) from this youtube video:
#https://www.youtube.com/watch?v=WTLPmUHTPqo  
#Channel "Tech with Tim", video: "Planet Simulation in Python - Tutorial"

#After that, I added the outer planets Jupiter, Saturn, and Neptune.
#Then I made an upper limit to the number of positions recorded in the orbits list so that the sim wouldn't start slowing down after awhile.
#I modified the view settings and made key handling so you could zoom in and out with + or = and - (minus).
#I modified a few colors and then went out and found neat links for reading facts about the various planets.
#Finally, I made a ton of comments.  Hopefully it might help some python beginners or otherwise make the planetarium sim more
#approachable for people who want to play with it, programmers or otherwise.

import pygame
import math
pygame.init()

#WIDTH, HEIGHT = 800, 800
WIDTH, HEIGHT = 1920, 1080
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("My solar system")

WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
DARK_GRAY = (80, 78, 81)
BLACK = (0, 0, 0)
JUPITER_PURPLE = (106, 81, 119)
FONT = pygame.font.SysFont("comicsans", 16)

orbit_list_max_length = 5000
inner_planets = ["Mercury", "Venus", "Earth", "Mars", "Jupiter"]

class Planet:
	AU = (149.6e6 * 1000)  #an AU = 149.6 million km, * 1000 converts it to meters
	G = 6.67428e-11
	#Default setting, only shows up to Jupiter:  SCALE = 250 / AU # 1 AU = 100 pixels
	SCALE_NUMERATOR = 30 	# this shows some of Neptune's orbit
	SCALE = SCALE_NUMERATOR / AU
	# to zoom out, make the number smaller - this will fit more planets
	TIMESTEP = 3600 * 24 # 1 day: (seconds in one hour = 3600, * 24 = one day)
	position_update_counter = 0

	def __init__(self, name, x, y, radius, color, mass):
		self.name = name
		#x and y are in meters
		self.x = x
		self.y = y
		self.radius = radius
		self.color = color
		self.mass = mass

		self.orbit = [] # in order to draw a circular orbit
				# as we move it around (we will record points)
		self.sun = False
		self.distance_to_sun = 0

		self.x_vel = 0
		self.y_vel = 0

	def draw(self, win):
		x = self.x * self.SCALE + WIDTH / 2 # convert to pixels for drawing
		y = self.y * self.SCALE + HEIGHT / 2  # makes it much smaller to fit scrn

		if len(self.orbit) > 2:
			updated_points = []
			for point in self.orbit:
				px, py = point
				px = px * self.SCALE + WIDTH / 2
				py = py * self.SCALE + HEIGHT / 2
				updated_points.append((px, py))

			pygame.draw.lines(win, self.color, False, updated_points, 2)

		pygame.draw.circle(win, self.color, (x, y), self.SCALE_NUMERATOR * .008  * self.radius)

		if not self.sun:
			distance_text = FONT.render(f"{round(self.distance_to_sun/1000, 1)}km", 1, WHITE)
			win.blit(distance_text, (x - distance_text.get_width()/2, y - distance_text.get_width()/2))

	def attraction(self, other):  # other is some other planet
		other_x, other_y = other.x, other.y
		distance_x = other_x - self.x
		distance_y = other_y - self.y

		distance = math.sqrt(distance_x ** 2 + distance_y ** 2)

		if other.sun:
			self.distance_to_sun = distance

		force = self.G * self.mass * other.mass / distance**2
		# this is r, or the straight line force...now break into x and y force

		theta = math.atan2(distance_y, distance_x)
		force_x = math.cos(theta) * force
		force_y = math.sin(theta) * force

		return force_x, force_y

# F = G * (Mm / radius^2)  
#   where M is mass of sun, m is mass of planet, 
#   radius is distance of planet to sun, G is force of gravity
# we break the force F into x and y directions
#	by taking the x and y positions and get r by x^2 + y^2 = r^2 (Pythagorean equation)
#	we get angle theta of that x, y and r triangle by taking arc tan ( y / x )
#	tan theta = opposite / adjacent -> opp is y, adj is x, isolate for theta = arctan

	def update_position(self, planets):
		total_fx = total_fy = 0
		for planet in planets:
			if self == planet:
				continue # trying to calculate distance with self would
					# give a divide by zero error
			fx, fy = self.attraction(planet)
			total_fx += fx
			total_fy += fy

		self.x_vel += total_fx / self.mass * self.TIMESTEP  # f = ma
		self.y_vel += total_fy / self.mass * self.TIMESTEP

		# F = m / a   (F is the self.mass * acceleration)
		# increasing self velocity by F

		# Now that we have velocity, let's increment positions:
		self.x += self.x_vel * self.TIMESTEP
		self.y += self.y_vel * self.TIMESTEP

		# Remove very old elements of the orbital position tracking list
		# This should keep the simulation from slowing down too much
		if len(self.orbit) > orbit_list_max_length:
			del(self.orbit[0])

		# Keep track of how many times we've called this function so that we can update orbital position
		# list appropriately (on the outer planets, we'll do it only once every 13 times through the loop
		# because that gives a bit under 5K entries for Neptune's 60190 day orbital periody, meaning
		# that we'll see orbital lines going all the way around without a gap)
		Planet.position_update_counter += 1

		# record the position so we can draw the orbital lines
		if self.name in inner_planets:
			self.orbit.append((self.x, self.y))  #update inner planets' orbital positions every time
		elif Planet.position_update_counter %13 == 0:
			self.orbit.append((self.x, self.y)) #update further planets' orbital positions once every 13 times
#		else:
#			print(str(Planet.position_update_counter) + " % " + str(13) + ": " + str(Planet.position_update_counter % 13))

		if Planet.position_update_counter > 5000:
			Planet.position_update_counter = 0

#		print(Planet.position_update_counter)

# SOH CAH TOA:

# Sin theta = opp / hyp  or  y / r  or Fy / Force

def main():
	run = True
	clock = pygame.time.Clock()

	#How to make a planet in this simulator:  Use this function signature, see the examples below:
	#Planet(name, x_pos, y_pos, radius, color, mass) -> x_pos is distance to the sun (if on y = 0 line)
	#Give your planet an initial velocity for the y value, this will only work if you put the planet on the y=0 line to start.
	#Due to the way the update_position works, we only have to give a single velocity and it will start calculating both x & y velocities.
	#This value will be in meters per second, for a list of real planetary velocities around the sun, see this link:
	#https://planetfacts.org/orbital-speed-of-planets-in-order/

	#To find some of the colors, I just searched for "color of jupiter in RGB" or "average color of neptune in RGB", etc (red, green, blue)
	#It should be defined with the parenthesis, like this:  my_color = (100, 100, 100)

	#My radius estimations are VERY rough.  Apologies.  I looked up the radiuses, multiplied them by 2 for diameter, then did a very rough
	#comparison with the sun's diameter and then guestimated a value.  That's all I did.
	#Feel free to play with the values.  If you do that, you can also play around
	#with the line in Planet.draw(): "pygame.draw.circle(win, self.color, (x, y), self.SCALE_NUMERATOR * .008  * self.radius)"

	#Finally, I found masses just by searching like this: "jupiter mass in kilograms" or "jupiter mass in kg".
	#The result is like: "1.898 × 10²⁷ kg", which becomes 1.898 * 10**27 or rounded up to 1.90 * 10**27
	
	#Make sure to add any new planets' variable you define to the planets list (doesn't matter what order).
	sun = Planet("sun", 0, 0, 30, YELLOW, 1.98892 * 10**30) # mass is in kilograms (kg)
	sun.sun = True

	#Note:  One cool way to get help with exponential notation in expressions is:  
	#https://www.symbolab.com/solver/simplify-calculator/simplify

	earth_distance_to_sun = -1 * Planet.AU # -1 puts it to the left of the sun, 1 to the right

	#FYI:  Mercury's orbital period, the time it takes to fully orbit the sun in Earth days, is 88 days
	#https://science.nasa.gov/mercury/facts/
	mercury = Planet("Mercury", 0.387 * Planet.AU, 0, 8, DARK_GRAY, 3.30 * 10**23)
	mercury.y_vel = -47.4 * 1000  #if you put the planet to the right of the sun, in order to orbit clockwise, the velocity must be negative
	# otherwise, if it's on the left, to orbit clockwise, velocity will be positive...for counterclockwise, reverse these.

	#Venus's orbital period is 224.7 Earth days
	#https://science.nasa.gov/venus/venus-facts/
	venus = Planet("Venus", 0.723 * Planet.AU, 0, 14, WHITE, 4.8685 * 10**24)
	venus.y_vel = -35.02 * 1000

	#Earth's orbital period is 365.26 Earth days = one Earth "year"
	#https://science.nasa.gov/earth/facts
	#https://science.nasa.gov/resource/earth-poster-version-c/
	#https://earth.google.com/
	earth = Planet("Earth", -1 * Planet.AU, 0, 16, BLUE, 5.9742 * 10**24)
	earth.y_vel = 29.783 * 1000 # km per second * 1000 which gives us meters per second

	#This paragraph of code just isn't working yet, more debugging needed, but probably can't properly keep the moon in orbit around
	#the earth with only one position update per "day" of simulation time...it's probably speeding off into infinity right now
	earth_to_moon_distance = 385000 * 1000 # the average distance from the center of earth to the center of the moon is 385,000 kilometers.  Multiply by 1000 to get meters.
	earth_diameter = 6378 * 2 * 1000 #earth radius is 6378 kilometers, diameter is 2 * radius, to get meters multiply kilometers by 1000.
	moon_diameter = 1737.5 * 2 * 1000 #moon radius is 1737.5 kilometers (converted to diameter then converted from km to meters)
	# earth_diameter / moon_diameter is roughly 3.67.  So the earth is roughly 3.67 times as wide as the moon.  So we'll give the moon a radius of 4...not exact but close.
	earth_moon = Planet("Luna", -1 * Planet.AU + earth_to_moon_distance, 0, 4, WHITE, 1.619 * 10**23)
	# since I'm just adding the distances together, I'll set the moon's orbital velocity to Earth's + the rate
	# that the moon orbits Earth.  Hopefully this simulation updates often enough to keep the moon in orbit
	# around the Earth, but if simulation update frequency is 1 earth day, I kind of doubt it...it'll probably
	# fling off in some random direction....we'll see.
	moon_earth_orbital_vel = 1.023055556 * 1000 # meters per second
	# to get the above, I took 3,683 km/hr, divided by 3600 seconds / hr to get 1.023055556 km / sec,
	# then multiplied by 1000 to get meters per second
	earth_moon.y_vel = earth.y_vel + moon_earth_orbital_vel

	#Mar's orbital period is 687 Earth days
	#https://science.nasa.gov/mars/facts/
	mars = Planet("Mars", -1.524 * Planet.AU, 0, 12, RED, 6.39 * 10**23)
	mars.y_vel = 24.077 * 1000

	#Jupiter's orbital period is 4,333 Earth days
	#https://science.nasa.gov/jupiter/jupiter-facts/
	jupiter = Planet("Jupiter", 5.20 * Planet.AU, 0, 22, JUPITER_PURPLE, 1.90 * 10**27)
	jupiter.y_vel = 13.07 * 1000

	#Saturn's orbital period is 10,759 Earth days
	#https://science.nasa.gov/saturn/facts/
	SATURN_PALE_YELLOW = (250, 229, 191) # saturn's average rgb color
	saturn = Planet("Saturn", 9.5 * Planet.AU, 0, 20, SATURN_PALE_YELLOW, 1.25 * 10**27)
	saturn.y_vel = 9.69 * 1000

	#Neptune's orbital period is approximately 60,190 Earth days
	#https://science.nasa.gov/neptune/neptune-facts/
	NEPTUNE_BLUE = (46, 93, 157)
	neptune = Planet("Neptune", 30 * Planet.AU, 0, 18, NEPTUNE_BLUE, 2.258 * 10**26) 
	# the circle radiuses are MORE than rough and not great at indicating relative sizes, though I kind of tried
	neptune.y_vel = 5.43 * 1000

	planets = [sun, mercury, venus, earth, mars, jupiter, saturn, neptune]

	while run:
		clock.tick(60)
		WIN.fill(BLACK)

		#https://www.pygame.org/docs/ref/key.html
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
			if event.type == pygame.KEYUP:
				# my laptop's keyboard has + and = on the same key, have to press shift to get '+'.
				if event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
					Planet.SCALE_NUMERATOR = Planet.SCALE_NUMERATOR + 5
					Planet.SCALE = Planet.SCALE_NUMERATOR / Planet.AU
					print("Planet.SCALE_NUMERATOR: " + str(Planet.SCALE_NUMERATOR))
				if event.key == pygame.K_MINUS:
					Planet.SCALE_NUMERATOR = Planet.SCALE_NUMERATOR - 5
					Planet.SCALE = Planet.SCALE_NUMERATOR / Planet.AU
					print("Planet.SCALE_NUMERATOR: " + str(Planet.SCALE_NUMERATOR))

		for planet in planets:
			if not planet.sun:
				planet.update_position(planets)
			planet.draw(WIN)

#		if len(planets[1].orbit) > 3:
#			print("Orbits len: " + str(len(planets[1].orbit)))

		pygame.display.update()

	pygame.quit()

main()
