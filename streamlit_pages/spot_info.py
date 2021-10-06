import streamlit as st
from PIL import Image


def app():
    st.write("""
    ## Top 10 spots
    """)
    st.write("""
    ### Nazaré / Praia do Norte
    """)

    imagen = Image.open("images/nazare.jpg")
    imagen2 = Image.open("images/praia.jpg")
    
    st.image(imagen, use_column_width=True)
    st.image(imagen2, use_column_width=True)
    
    st.write("Nazare in North Portugal is an exposed beach break that has quite reliable surf and can work at any time of the year. The best wind direction is from the east. Windswells and groundswells in equal measure and the ideal swell direction is from the west. The beach break offers both left and right hand waves. Surfable at all stages of the tide. It very rarely gets crowded here.")

    st.write("""
    ### Pipeline / Backdoor
    """)
    imagen3 = Image.open("images/pipe.jpg")
    
    st.image(imagen3, use_column_width=True)

    st.write("Backdoor was somewhat ignored during Pipeline's first golden days in the 1970s. It makes you wonder how many heaving barrels roared right off the peak before everyone kind of clicked on it. The wave relies on a slight breaking up of swell lines from the northwest (shorter to mid period swells are best, of a swell combo) and a thin channel between the Pipe reef and Off-The-Wall. The broken swell allows a tapering wall, which hits square on the shallowest part of first reef and creates an intense and very hollow, deep tube. Further inside, the reef gets shallower and actually pokes itself above the waterline here and there. Dealing properly with the finish of a ride is very important, as it will often end as a powerful closeout. This is even more the case on larger days, when the unwary surfer might come out of the tube, start paddling, and be faced with a several closeouts sections on the head over very shallow and sharp reef -- one of the North Shore's scariest moments. This is especially true upon completion on the first wave of a set, and during the more westerly swells where the current is pulling you across the impact zone of Backdoor and then inside of Pipe. If caught in this situation, either paddle in to the beach or go with the current and paddle over to the channel next to Pipe to get back out.")

    st.write("""
    ### El Fronton
    """)
    imagen4 = Image.open("images/fronton.jpeg")
    st.image(imagen4, use_column_width=True)
    st.write("El Fronton in Gran Canaria is an exposed reef break that has dependable surf, although summer tends to be mostly flat. Ideal winds are from the south. Windswells and groundswells in equal measure and the optimum swell angle is from the northwest. Best around low tide. It's often crowded here. Beware of rocks, hevy wave")

    st.write("""
    ### Puerto Escondido
    """)
    imagen5 = Image.open("images/puerto.jpg")
    st.image(imagen5, use_column_width=True)
    st.write("Commonly known as the Mexican Pipeline it's not a random coincidence that this heavily photographed spot is compared to another gigantic, awe-inspiring, fearsome Pacific wave. A deep off-shore trench helps focus and amplify southerly swells, which explains why Puerto's two main waves (a left called Far Bar and a right called Carmelita's) seldom dip under head high all summer and occasionally max out at 40- to 60-foot faces. Despite breaking over a sandy bottom fairly close to shore, when it's big, you better know what you're doing out there. Hazards include, but aren't limited to: strong currents, inescapable rips, and board-snapping duck dives. It's a minefield out there, but if you connect with the right wave, you'll know the true meaning of the word cavern")

    st.write("""
    ### The Box
    """)

    imagen6 = Image.open("images/box.jpg")
    st.image(imagen6, use_column_width=True)
    st.write("The Box is a thick, below sea level right-breaking mutant tube that is only for the very best, committed surfers. The Box throws out over hard flat rocks and is totally unforgiving.")

    st.write("""
    ### Itacoatiara
    """)

    imagen7 = Image.open("images/ita.jpg")
    st.image(imagen7, use_column_width=True)
    
    st.write("Itacoatiara in Rio de Janeiro is an exposed beach reef and point break that has dependable surf, although summer tends to be mostly flat. The best wind direction is from the north with some shelter here from east winds. Most of the surf here comes from groundswells and the ideal swell direction is from the southwest. The left reef break is best, but there is a right reef too.. It's often crowded here. Hazards include crowds, rips.")

    st.write("""
    ## Padang-Padang
    """)

    imagen8 = Image.open("images/pp.jpg")
    st.image(imagen8, use_column_width=True)

    st.write("Padang Padang in Bali (The Bukit) is a fairly exposed reef break that has inconsistent surf. May-Oct (Dry Season) is the best time of year for waves. The best wind direction is from the southeast. Most of the surf here comes from groundswells and the ideal swell direction is from the southwest.. Best around mid tide. When it's working here, it can get crowded. Rocks are a hazard.")


    st.write("""
    ### Mosca Point
    """)
    imagen9 = Image.open("images/mosca.jpg")
    st.image(imagen9, use_column_width=True)
    st.write("Mosca Point in Gran Canaria is a sheltered beach and reef break that has quite consistent surf. Autumn and winter are the best times of year for waves. The best wind direction is from the north. Windswells and groundswells in equal measure and the ideal swell direction is from the north. The beach breaks offer lefts and rights. Best around low tide. When it's working here, it can get crowded. Hazards include rocks, man-made danger (buoys etc...) and locals.")

    st.write("""
    ### Tauro
    """)

    imagen10 = Image.open("images/tauro.jpeg")
    st.image(imagen10, use_column_width=True)
    st.write("Tauro, a seculuded slab found in the south of Gran Canaria. Works best when the swell direction is as west as possible(As Tenerife is in front). Usually not affected by wind, although west winds make the wave choppy. Heavily crowded and localized. Not recommended for novices")

    st.write("""
    ### Mundaka
    """)
    imagen11 = Image.open("images/mundaka.jpg")
    st.image(imagen11, use_column_width=True)
    st.write("The combination of river and oceanic currents have sculpted a sandbank of almost mathematical perfection to produce one of the most awesome waves on the planet. Access is simple enough, a gentle paddle from the harbor, but this isn't an easy wave to surf. The water detonates onto the shallow sand bank in a steep and pitching lunge, and although it is sand-bottomed, from here on in it breaks like a reef. Those who hit the bottom do so hard. The outer peak is dominated by a pack, but even the scraps way down the line can offer great barrels. Mundaka's fantastically shaped rivermouth sandbar creates solid, 200-yard-long, top-to-bottom barrels. The rip that runs along the side of the cliff is perhaps surfing's ultimate saltwatery escalator -- it's a paddle-optional trip straight to the peak. Mundaka's essentially a 200-yard-long shorebreak wave. It gulps and warbles and barrels top-to-bottom like the best inside beachbreak ever and keeps going. When you finish the wave -- especially when it's bigger -- it's best to prone out and head back over toward the cliff rip rather than kick out and paddle back along the edge of the wave.")
    

