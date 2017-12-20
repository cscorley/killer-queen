from hello.models import RandomName


names= """mufflestar
banterchips
dribblerushers
gobblesparks
mumblejammers
dazzlewishers
bubblecorks
murmurchins
quibblewills
jiggletwigs
dibbleknots
fumbletales
dribblejokes
bundlepitches
slumberbeans
flitterleafs
grapplecorks
doodlestrips
gigglechins
janglestars
dribbledishes
riddledolls
bubblebits
dibbletails
jostlehearts
rumblebands
spattlegifts
pedaltips
twittersides
mutterbells
crumblesides
fiddlespots
puddlejams
whistlecheeks
bubbleleaves
spitterchests
riddlerubs
blatherclouds
ponderslides
mumbledishes
sprinklelinks
grappletwigs
pedalstraws
paddlemarks
twinkleshinies
dallyrubs
jabberrings
splutterkisses
mumbleclouds
"""

random_names = list()
for name in names.splitlines():
    name = name.title()
    if RandomName.objects.filter(name=name).first():
        continue

    random_names.append(RandomName(name=name))

RandomName.objects.bulk_create(random_names)