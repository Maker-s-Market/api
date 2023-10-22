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

    bau_monocastas_adegamae = Product(id=str(uuid4()), name="Bau Monocastas AdegaMãe",
                                      description="A Norte de Lisboa e a um passo da costa oceânica, a AdegaMãe potencia um terroir  fortemente influenciado pelas " +
                                                  "brisas marítimas predominantes, destacando-se pelos seus vinhos de "
                                                  "inspiração atlântica,plenos de carácter, frescos e minerais, premiados a nível nacional e internacional." +
                                                  "Contém:" +
                                                  "1 Gf Vinho Branco Sauvignon Blanc 2020" +
                                                  "1 Gf Vinho Branco Alvarinho 2020" +
                                                  "1 Gf Vinho Tinto Pinot Noir 2019" +
                                                  "1 Gf Vinho Tinto Syrah 2019" +
                                                  "1 Gf Vinho Tinto Touriga Nacional 2019" +
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

    torre_de_aprendizagem = Product(id=str(uuid4()), name="Torre de Aprendizagem",
                                    description="A torre de aprendizagem é um móvel que permite que as crianças participem nas atividades do dia a dia, " +
                                                "de forma segura e autónoma.",
                                    price=150.00, stockable=True, stock=10, discount=0.0,
                                    image="https://www.creative-gourmet.com/cdn/shop/products/Pack4CervejasSovinacopy_5000x.jpg?v=1601935894",
                                    number_views=5, categories=[home, for_kids_and_babies, toys_and_games])

    velas = Product(id=str(uuid4()), name="Velas de Natal",
                    description="Velas aromatizadas com decorações de Natal, para acentuar o espírito natalício.",
                    price=10.00, stockable=True, stock=20, discount=0.0,
                    image="https://hoosierhomemade.com/wp-content/uploads/DIY-Christmas-Candles-FEATURE.jpg",
                    number_views=15, categories=[home, candles_and_air_fresheners])

    mesa = Product(id=str(uuid4()), name="Mesa ao Ar Livre",
                   description="Mesa construida utilizando paletes, e topo de vidro. Não inclui cadeiras.",
                   price=200.00, stockable=False, stock=0, discount=0.0,
                   image="https://i.pinimg.com/736x/89/42/e2/8942e2a144b37373f01f94149606a721.jpg",
                   number_views=8, categories=[home])

    espanta_espiritos = Product(id=str(uuid4()), name="Espanta-Espíritos",
                                description="Espanta-Espíritos, feitos com madeira de bambu resinada com 6 canas, para criar um ambiente relaxador em dias ventosos.",
                                price=20.00, stockable=True, stock=30, discount=0.0,
                                image="https://cdn.shopk.it/usercontent/valentina-body-care/media/images/e4081fd-115939-20220131_160707.jpg",
                                number_views=6, categories=[home])

    db.add_all([torre_de_aprendizagem, velas, mesa, espanta_espiritos])

    cavalinho = Product(id=str(uuid4()), name="Cavalinho de madeira",
                        description="Haverá brinquedo que nos transporte mais à nossa infância? De madeira, bem simples, o cavalinho de \
                            madeira é um objeto decorativo bonito para quarto do bebé e super divertido para crianças.   \
                            Tem pegas e repouso de pés para a criança se poder equilibrar e assim disfrutar em maior segurança.",
                        price=45.00, stockable=True, stock=5, discount=0.0,
                        image="https://www.babytower.pt/cdn/shop/products/IMG_0407_1024x1024.jpg?v=1642445587",
                        number_views=6, categories=[for_kids_and_babies])

    pecas_madeira = Product(id=str(uuid4()), name="Jogo de madeira",
                            description="Simples e clássico, o ato de empilhar e arranjar blocos de madeira de diferentes formas e cores torna-se numa atividade " \
                                        "divertida para crianças e bebés. O jogo de madeira oferece diferentes formas de peças, existindo inumeras possibilidades " \
                                        "de as arranjar.",
                            price=10.00, stockable=True, stock=40, discount=10.0,
                            image="https://ae01.alicdn.com/kf/H9c89f7aa3fde495d8671485db37e9640Q/Madeira-Blocos-Forma-Sorter-Walking-Pull-Along-Car-Model-Handmade-modelo-brinquedo-Educacional-Kids-Toy-Shape.jpg",
                            number_views=5, categories=[for_kids_and_babies])

    pantufas = Product(id=str(uuid4()), name="Pantufas de lã",
                       description="Pantufas quentinhas feitas à mão, de lã macia e confortáveis para uso interior, em fio de malha. Deve disponibilizar o tamanho para fazer.",
                       price=12.00, stockable=False, stock=0, discount=0.0,
                       image="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQU99YekSEGlHfNq99Xlk4qHCy9zUn2DxZdT4sVy7gmFjYuZp_pNwE9-8vNDvDr19PbVDw&usqp=CAU",
                       number_views=5, categories=[for_kids_and_babies])

    db.add_all([cavalinho, pecas_madeira, pantufas])

    jenga = Product(id=str(uuid4()), name="Jogo Jenga",
                    description="Jenga é um jogo 2 para 2 com peças de madeira onde a cada turno, um jogador deverá tirar uma peça da plataforma sem que esta se desmorone. \
                        O jogador que fizer demoronar a plataforma, perde. \
                        Bastante enternecedor, o jogo Jenga é excelente para entreter não só crianças, como adultos também.",
                    price=5.00, stockable=True, stock=20, discount=0.0,
                    image="https://www.globalcraftsb2b.com/cdn/shop/products/2959b4cf-a696-43b3-a6e3-339a65417a78_2000x.jpg?v=1656437009",
                    number_views=16, categories=[toys_and_games, for_kids_and_babies])

    ludo = Product(id=str(uuid4()), name="Jogo Ludo Madeira",
                   description="Ludo é um jogo de estratégia para dois a quatro jogadores, no qual os jogadores competem com suas quatro fichas do início ao fim de acordo com os lançamentos de um único dado." \
                               "Tabuleiro e peças feitas em madeira, com dado incluido.",
                   price=20.00, stockable=True, stock=5, discount=0.0,
                   image="https://i.pinimg.com/736x/c2/b3/2c/c2b32cbb0a953022b101af834e2f63bf.jpg",
                   number_views=9, categories=[toys_and_games])

    xadrez = Product(id=str(uuid4()), name="Jogo Xadrez",
                     description="Clássico jogo de Xadrez feito em madeira, com peças também em madeira pintada com tinta acrilica, revestida com resina",
                     price=40.00, stockable=False, stock=0, discount=0.0,
                     image="https://ae01.alicdn.com/kf/Heb5ba19c76b94b2089ee20b09940ce7dT.jpg_640x640Q90.jpg_.webp",
                     number_views=22, categories=[toys_and_games])

    damas = Product(id=str(uuid4()), name="Jogo Damas",
                    description="Jogo de damas em madeira, com peças também em madeira pintada com tinta acrilica, revestida com resina",
                    price=20.00, stockable=False, stock=0, discount=0.0,
                    image="https://i.ytimg.com/vi/H9_MvwDOT4M/maxresdefault.jpg",
                    number_views=12, categories=[toys_and_games])

    db.add_all([jenga, ludo, xadrez, damas])

    pulseiras_amizade = Product(id=str(uuid4()), name="Pulseiras da Amizade",
                                description="Pulseiras de diferentes tipo, com missangas, nome em fio ou outras decorações",
                                price=3.00, stockable=False, stock=0, discount=0.0,
                                image="https://img.fruugo.com/product/1/87/421566871_max.jpg",
                                number_views=6, categories=[diy_crafts, jewelry_and_accessories])

    caixa_lencos = Product(id=str(uuid4()), name="Caixa de Lenços",
                           description="Caixinha de lenços pintada manualmente, de madeira. Mensagem nas caixas é personalizável.",
                           price=8.00, stockable=True, stock=13, discount=0.0,
                           image="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRpPDiG1Ckp6KgeHgCKR8zPPSeWUU6T4djCbg&usqp=CAU",
                           number_views=2, categories=[diy_crafts])

    saco_malha = Product(id=str(uuid4()), name="Saco em malha",
                         description="Saco simples de malha crochê colorido",
                         price=15.00, stockable=False, stock=0, discount=0.0,
                         image="https://4.bp.blogspot.com/-2PkVkDZqPo4/WJS7OysQgWI/AAAAAAAABDI/YqALSVruZKwGJr6ZgN53gl_IMw9MFYYtQCLcB/s1600/sac%2Bqud1.jpg",
                         number_views=15, categories=[diy_crafts])

    toalhas_mesa = Product(id=str(uuid4()), name="Toalha de mesa",
                           description="Toalha de mesa com bordas e figuras em renda",
                           price=20.00, stockable=False, stock=0, discount=0.0,
                           image="https://areliquia.pt/wp-content/uploads/2023/04/A03913_1-4.jpg",
                           number_views=12, categories=[diy_crafts, home])

    almofada = Product(id=str(uuid4()), name="Almofada",
                       description="Hand-Woven Almofada De Lã Grossa Cheio de Fio De Tecido De Algodão, Sofá Cadeira Almofada, Cintura Travesseiro, Novo Estilo",
                       price=27.45, stockable=True, stock=50, discount=3,
                       image="https://ae01.alicdn.com/kf/Hd920f7510cef4bbbb4824418874ddc41G/Hand-Woven-Almofada-De-L-Grossa-Cheio-de-Fio-De-Tecido-De-Algod-o-Sof-Cadeira.jpg",
                       number_views=2, categories=[diy_crafts, home])

    db.add_all([pulseiras_amizade, caixa_lencos, saco_malha, toalhas_mesa, almofada])

    bolo_aniversario = Product(id=str(uuid4()), name="Bolo de Aniversário",
                               description="Bolo de aniversário feito à mão e personalizado, design acordado com o utilizador.",
                               price=20.00, stockable=False, stock=0, discount=0.0,
                               image="https://docespaladares.com/wp-content/uploads/2019/04/2702-510x383.jpg",
                               number_views=10, categories=[stationery_and_party_supplies])

    porta_chaves = Product(id=str(uuid4()), name="Porta-Chaves",
                           description="Estes chaveiros são totalmente feitos à mão, com lindos motivos bordados. Embelezado com borlas e miçangas ou só com tecido.",
                           price=4.00, stockable=True, stock=50, discount=0.0,
                           image="https://ghabakala.com/wp-content/uploads/2022/12/Ghabakala_SKUKEYCHAIN04_Handcrafted-Keychain01.jpg",
                           number_views=16, categories=[stationery_and_party_supplies, diy_crafts])

    cartoes_aniversario = Product(id=str(uuid4()), name="Cartões para Festa",
                                  description="Cartões para festas de aniversário, casamentos, batizados e outras ocasiões.",
                                  price=4.00, stockable=False, stock=0, discount=0.0,
                                  image="https://www.dhresource.com/0x0/f2/albu/g9/M00/AD/D5/rBVaVV2vC12AVuUMAAXGxBxxNj8736.jpg",
                                  number_views=7, categories=[stationery_and_party_supplies, diy_crafts])

    nomes_madeira = Product(id=str(uuid4()), name="Nomes de madeira personalizados",
                            description="Nomes de madeira personalizados, com diferentes tipos de letra e cores",
                            price=12.95, stockable=False, stock=0, discount=0.0,
                            image="https://m.media-amazon.com/images/I/619E86zfqqL._SL1000_.jpg",
                            number_views=2, categories=[diy_crafts, home])

    db.add_all([bolo_aniversario, porta_chaves, nomes_madeira, cartoes_aniversario])

    brincos = Product(id=str(uuid4()), name="Brincos",
                      description="Brincos personalizados, decorados com missangas, fio e outros motivos.",
                      price=7.50, stockable=False, stock=0, discount=0.0,
                      image="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSkP_Zl8l6N-sgNzxOHc3g1MzH-lhGiAXLKM-js3W2AAznUKj7LhK63oVs71smYaabsF70&usqp=CAU",
                      number_views=0, categories=[jewelry_and_accessories])

    colares = Product(id=str(uuid4()), name="Colares",
                      description="Colares personalizados, decorados com missangas ou outro motivo, com fio de aço inoxidável ou linha.",
                      price=7.50, stockable=False, stock=0, discount=0.0,
                      image="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSkP_Zl8l6N-sgNzxOHc3g1MzH-lhGiAXLKM-js3W2AAznUKj7LhK63oVs71smYaabsF70&usqp=CAU",
                      number_views=0, categories=[jewelry_and_accessories])

    db.add_all([brincos, colares])

    Corda_cao = Product(id=str(uuid4()), name="Corda para cão",
                        description="Corda para cão, feita à mão com diferentes cores e tamanhos",
                        price=4.05, stockable=False, stock=0, discount=0.0,
                        image="https://static.zoomalia.com/prod_img/61824/lm_276db8e1af0cb3aca1ae2d00186242045291571142472.jpg",
                        number_views=2, categories=[animals_and_plants])

    Cacto = Product(id=str(uuid4()), name="Cacto Artificial Opuntia 72 cm",
                    description="Cacto artificial com 72 cm de altura, com vaso de cerâmica",
                    price=32.95, stockable=True, stock=50, discount=3,
                    image="https://cdn.sklum.com/pt/wk/2426848/cacto-artificial-opuntia-72-cm.jpg?cf-resize=gallery",
                    number_views=2, categories=[animals_and_plants, home])

    db.add_all([Corda_cao, Cacto])
    caneca = Product(id=str(uuid4()), name="Caneca de Cerâmica",
                     description="Todas as canecas são feitas e pintadas à mão em cerâmica. Podem apresentar variações no seu formato, tamanho e detalhe entre eles. Caneca artesanal feita à mão ideal para  que desfrute de um bom café ou chá.",
                     price=6.00, stockable=True, stock=100, discount=0.0,
                     image="https://i.pinimg.com/736x/6a/f3/76/6af376dea1e08739412a5fe65c713cef.jpg",
                     number_views=2, categories=[piece_of_crockery, home])

    jarra = Product(id=str(uuid4()), name="Jarra de Cerâmica",
                    description="Todas as jarras são feitas e pintadas à mão em cerâmica. Podem apresentar variações no seu formato, tamanho e detalhe entre eles. Jarra artesanal feita à mão ideal para  que desfrute de um bom café ou chá.",
                    price=45, stockable=True, stock=150, discount=0.0,
                    image="https://cdn.sklum.com/pt/wk/2386935/vaso-de-ceramica-dalita.jpg?cf-resize=gallery",
                    number_views=2, categories=[piece_of_crockery, home])

    db.add_all([caneca, jarra])
    cabaca = Product(id=str(uuid4()), name="Cabaça Pintada",
                     description="Cabaça pintada com tinta acrílica e envolvida por uma camada de resina, para decoração de exteriores em ambientes mais rústicos",
                     price=20.00, stockable=True, stock=5, discount=0.0,
                     image="https://comofazerfacil1001ideias.com/wp-content/uploads/2018/02/Ideias-para-decorar-caba%C3%A7as.jpg",
                     number_views=2, categories=[art, diy_crafts, home])

    azuleijo = Product(id=str(uuid4()), name="Azuleijo Pintado",
                       description="Azuleijo pintado com tinta acrílica e envolvida por uma camada de resina, para decoração de exteriores em ambientes mais rústicos",
                       price=20.00, stockable=False, stock=0, discount=0.0,
                       image="https://www.casadart.pt/wp-content/uploads/2016/07/Azulejo-Tradicional-Espanhol-Parede.jpg",
                       number_views=2, categories=[art, diy_crafts, home])

    ceramica = Product(id=str(uuid4()), name="Peça de Cerâmica",
                       description="Peça de cerâmica pintada com tinta acrílica e envolvida por uma camada de resina, para decoração de exteriores em ambientes mais rústicos",
                       price=20.00, stockable=False, stock=0, discount=0.0,
                       image="https://www.rostosdaaldeia.pt/wp-content/uploads/2022/03/ceramica-celia-macedo-corval.jpg",
                       number_views=2, categories=[art, home, piece_of_crockery])

    db.add_all([cabaca, azuleijo, ceramica])

    candle_mediterranean = Product(id=str(uuid4()), name="Vela Mediterrânea",
                                   description="Natural soy and coconut scented wax candle. " +
                                               "<br> The MEDITERRANEAN scented candle is the perfect complement for a relaxing moment. Its refreshing and marine notes will remind you of nature in your own home. Composed of vegan soy and coconut wax, put together in a glass container in which the adhesives have been reduced to ensure the possibility of reuse once the product runs out. ",
                                   price=23.99, stockable=True, stock=200, discount=0.0,
                                   image="https://dareels.com/26292-large_default/candle-mediterranean.jpg",
                                   number_views=10, categories=[candles_and_air_fresheners, home])
    incensos = Product(id=str(uuid4()), name="Incensos Mandalas Maracujá",
                       description="Incenso com aroma 12 unidades.",
                       price=2.00, stockable=True, stock=200, discount=0.0,
                       image="https://cdn.weasy.io/users/natura-store/catalog/022024330012.34_0.jpg",
                       number_views=7, categories=[candles_and_air_fresheners, home])

    sabonetes = Product(id=str(uuid4()), name="Sabonete 100% Azeite",
                        description="Este sabonete tem um aroma suave e cítrico, com notas a madeira.",
                        price=4.99, stockable=True, stock=200, discount=0.0,
                        image="https://www.atelierdosabao.com/cdn/shop/products/Sabonete100_Azeite-AtelierdoSabao_800x.jpg?v=1643738526",
                        number_views=3, categories=[candles_and_air_fresheners, home])

    db.add_all([candle_mediterranean, incensos, sabonetes])
    db.commit()

    return JSONResponse(status_code=201, content=jsonable_encoder({"message": "INSERT DATA SUCCESS"}))
