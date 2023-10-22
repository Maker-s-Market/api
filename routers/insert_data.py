from uuid import uuid4

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from requests import Session
from starlette.responses import JSONResponse

from db.database import get_db
from models.category import Category
from models.product import Product

router = APIRouter(tags=['Insert Data'])


@router.get("/insert_data")
async def insert_data(db: Session = Depends(get_db)):
    # CATEGORY
    drinks = Category(id=str(uuid4()), name="Drinks", icon="FaWineBottle", slug="drinks")
    food = Category(id=str(uuid4()), name="Food", icon="RiCake3Fill", slug="food")
    home = Category(id=str(uuid4()), name="Home", icon="FaHome", slug="home")
    for_kids_and_babies = Category(id=str(uuid4()), name="For kids and babies", icon="TbHorseToy",
                                   slug="forkidsandbabies")
    toys_and_games = Category(id=str(uuid4()), name="Toys and games", icon="FaDiceD20", slug="toysandgames")
    diy_crafts = Category(id=str(uuid4()), name="DIY crafts", icon="BsTools", slug="diycrafts")
    stationery_and_party_supplies = Category(id=str(uuid4()), name="Stationery and Party Supplies", icon="GiPartyHat",
                                             slug="stationeryandpartysupplies")
    jewelry_and_accessories = Category(id=str(uuid4()), name="Jewelry and Accessories", icon="GiEmeraldNecklace",
                                       slug="jewelryandaccessories")
    animals_and_plants = Category(id=str(uuid4()), name="Animals and Plants", icon="GiPottedPlant",
                                  slug="animalsandplants")
    piece_of_crockery = Category(id=str(uuid4()), name="Piece of crockery", icon="FaKitchenSet", slug="pieceofcrockery")
    art = Category(id=str(uuid4()), name="Art", icon="FaPaintBrush", slug="art")
    candles_and_air_fresheners = Category(id=str(uuid4()), name="Candles and Air Fresheners", icon="GiCandleLight",
                                          slug="candlesandairfresheners")

    db.add_all([drinks, food, home, for_kids_and_babies, toys_and_games, diy_crafts, stationery_and_party_supplies,
                jewelry_and_accessories, animals_and_plants, piece_of_crockery, art, candles_and_air_fresheners])
    db.commit()

    # PRODUCT
    # drinks
    bau_monocastas_adegamae = Product(id=str(uuid4()), name="Bau Monocastas AdegaMãe",
                                      description="A Norte de Lisboa e a um passo da costa oceânica, a AdegaMãe potencia um terroir  fortemente influenciado pelas " +
                                                  "brisas marítimas predominantes, destacando-se pelos seus vinhos de "
                                                  "inspiração atlântica,plenos de carácter, frescos e minerais, premiados a nível nacional e internacional." +
                                                  "Contém:" +
                                                  "1 Gf Vinho Branco Sauvignon Blanc 2020" +
                                                  "1 Gf Vinho Branco Alvarinho 2020" +
                                                  "1 Gf Vinho Tinto Pinot Noir 2019" +
                                                  "1 Gf Vinho Tinto Syrah 2019" +
                                                  "1 Gf Vinho Tinto Touriga Nacional 2019"+
                                                  "1 Gf Vinho Tinto Merlot 2019",
                                      price=110.00, stockable=True, stock=70, discount=0.0,
                                      image="https://www.creative-gourmet.com/cdn/shop/products/BauMonocastasAdegaMaeWebcopy_5000x.jpg?v=1679582444",
                                      number_views=5, categories=[drinks])
    ginjinjinha = Product(id=str(uuid4()), name="Ginjinjinha",
                            description="Ginjinjinha is a Portuguese liqueur made by infusing ginja berries, a sour cherry type, in alcohol (aguardente is used) and adding sugar together with other ingredients. " +
                                        "It is served in a shot form with a piece of the fruit in the bottom of the cup. " +
                                        "It is a favourite liqueur of many Portuguese and a typical drink in Lisbon, Alcobaça and Óbidos.",
                            price=12.50, stockable=True, stock=10, discount=10.0,
                            image="https://wetravelportugal.com/wp-content/uploads/ginjinha-portugal-1024x768.jpg",
                            number_views=5, categories=[drinks])

    cerveja_artesanal = Product(id=str(uuid4()), name="Cerveja Sovina - Pack 4",
                                description="Pack 4 cervejas artesanais Sovina.<br> Contém 4 garrafas de 33cl cada das seguintes cervejas: " +
                                            "Sovina Helles, Sovina Pilsner, Sovina IPA e Sovina Stout.",
                                price=12.90, stockable=True, stock=10, discount=10.0,
                                image="https://www.creative-gourmet.com/cdn/shop/products/Pack4CervejasSovinacopy_5000x.jpg?v=1601935894",
                                number_views=20, categories=[drinks])

    db.add_all([bau_monocastas_adegamae, ginjinjinha, cerveja_artesanal])
    # food
    packJams = Product(id=str(uuid4()), name="Set 4 Tiptree Special Edition Jams",
                       description="Set of 4 Tiptree special edition jams.<br> Includes 4 jars of 42g each of the " +
                                   "following flavors: Strawberry with Champagne, Apricot with Armagnac, Orange with Malt Whiskey" +
                                   " and Blueberry with Gin.",
                       price=12.50, stockable=True, stock=10, discount=10.0,
                       image="https://www.creative-gourmet.com/cdn/shop/products/4_Compotas_Tiptree_5000x.jpg?v=1570958543",
                       number_views=5, categories=[food])
    extra_pumpkin_jam = Product(id=str(uuid4()), name="Extra Pumpkin Jam",
                                description="Sweet pumpkin jam produced from old homemade recipes from S.Miguel with locally produced fruit.",
                                price=4.50, stockable=True, stock=10, discount=0.0,
                                image="https://www.creative-gourmet.com/cdn/shop/files/CompotadeAbobora_5000x.jpg?v=1689261980",
                                number_views=15, categories=[food])
    azeite = Product(id=str(uuid4()), name="Azeite Virgem Extra Ouro Líquido",
                     description="É o primeiro azeite transmontano com ouro adicionado, que confere um toque único e requintado a qualquer prato, "
                                 "para além das propriedades benéficas do ouro. No interior são visíveis os flocos reluzentes de ouro comestível de 23 quilates, "
                                 "que vai ao encontro das exigências dos palatos mais apurados.Feito a partir de azeitonas Verdeal transmontana, Madural, Cobrançosa"
                                 " e Cordovil é um azeite com um aroma bastante frutado, fresco, com notas de maçã, banana, frutos secos, um pouco de pimenta, e um "
                                 "agradável fim de boca.",
                     price=12.90, stockable=True, stock=10, discount=0.0,
                     image="https://www.creative-gourmet.com/cdn/shop/products/Ouro_Liquido_5000x.png?v=1499946795",
                     number_views=5, categories=[food])
    mel = Product(id=str(uuid4()), name="Mel Caseiro Multifloral (1Kg)",
                  description="Mel caseiro multifloral, produzido em Portugal, com um sabor doce e suave.",
                  price=15.00, stockable=True, stock=10, discount=0.0,
                  image="Mel Caseiro Multifloral (1Kg)",
                  number_views=2, categories=[food])

    rissois = Product(id=str(uuid4()), name="Rissóis de Camarão",
                      description="Rissóis de camarão, produzidos em Portugal, com um sabor doce e suave.",
                      price=15.00, stockable=False, stock=0, discount=0.0,
                      image="https://feed.continente.pt/media/puammcv3/rissois-de-camarao.jpg?anchor=center&mode=crop&width=1023&height=768&rnd=133129917583730000",
                      number_views=2, categories=[food])
    db.add_all([packJams, extra_pumpkin_jam, azeite, mel, rissois])
    # home
    torre_de_aprendizagem = Product(id=str(uuid4()), name="Torre de Aprendizagem",
                                    description="A torre de aprendizagem é um móvel que permite que as crianças participem nas atividades do dia a dia, " +
                                                "de forma segura e autónoma.",
                                    price=150.00, stockable=True, stock=10, discount=0.0,
                                    image="https://www.creative-gourmet.com/cdn/shop/products/Pack4CervejasSovinacopy_5000x.jpg?v=1601935894",
                                    number_views=5, categories=[home, for_kids_and_babies, toys_and_games])

    db.add_all([torre_de_aprendizagem])


    # for_kids_and_babies
    ## cavalinho de madeira - TbHorseToy

    # toys_and_games
    # diy_crafts
    # stationery_and_party_supplies
    # jewelry_and_accessories
    # animals_and_plants
    # piece_of_crockery
    # art
    # candles_and_air_fresheners

    return JSONResponse(status_code=201, content=jsonable_encoder({"message": "INSERT DATA SUCCESS"}))
