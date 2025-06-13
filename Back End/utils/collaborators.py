import math


class Author:
    def __init__(self, last_name: str, initials: str, author_id: int):
        self.last_name = last_name
        self.initials = initials
        self.id = author_id
        self.papers = []

    def __lt__(self, other):
        if self.last_name == other.last_name:
            return self.initials < other.initials
        return self.last_name < other.last_name

    def __repr__(self):
        return f"{self.initials} {self.last_name}"

    def __str__(self):
        return f"\nInitials: {self.initials}\n\
Last Name: {self.last_name}\n\
Papers: {self.papers}"

    def get_category(self):
        paper_categories = [
            paper.category for paper in self.papers if not math.isnan(paper.category)
        ]
        if not len(paper_categories):
            return math.nan
        else:
            return max(paper_categories, key=lambda x: paper_categories.count(x))
    
    def get_score(self):
        total_citations = sum([paper.citations for paper in self.papers])
        return total_citations//len(self.papers) 


class Paper:
    def __init__(
        self,
        paper_title: str,
        doi: str,
        category: float,
        citations: float,
        *authors: Author,
    ):
        def addPaper(paper: Paper):
            [author.papers.append(paper) for author in paper.authors]

        self.paper_title = paper_title
        self.id = doi
        self.authors = authors
        self.category = category
        self.citations = citations
        addPaper(self)

    def __repr__(self):
        return f"{self.paper_title}"

    def __str__(self):
        return f"\nPaper Title: {self.paper_title}\n\
Authors: {self.authors}\n"
