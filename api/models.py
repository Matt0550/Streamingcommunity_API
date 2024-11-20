from pydantic import BaseModel

class StreamingService(BaseModel):
    name: str
    url: str

class Episode(BaseModel):
    episodeNumber: str
    title: str
    urls: list[StreamingService] = None

class Season(BaseModel):
    season: str
    episodes: list[Episode]

class Genre(BaseModel):
    title: str
    url: str

    
class Show(BaseModel):
    id: str = None
    title: str = None
    url: str = None
    path: str = None
    image: str = None
    title_image: str = None
    background_images: list[str] = None
    description: str = None
    features: list[str] = None
    details: list[str] = None
    seasons: list[Season] = None


class ShowsResponse(BaseModel):
    category_title: str = None
    shows: list[Show] = None