import pandas as pd
from datetime import datetime


class Dataset:
    """
    Class for handling datasets containing both ideas and comments.
    """
    def __init__(self, path: str):
        self.path = path
        self.ideas_dict = {}
        self.comments = []
        self.load_ideas()
        self.load_comments()
        self.associate_comments_with_ideas()

    def load_ideas(self):
        """
        Parse ideas from the first sheet
        """
        ideas_table = pd.read_excel(self.path, sheet_name='ideas')
        for _, row in ideas_table.iterrows():
            idea = Idea(row)
            idea.check_required_ids()
            self.ideas_dict[idea.idea_id] = idea

    def load_comments(self):
        """
        Parse comments from the second sheet
        """
        comments_table = pd.read_excel(self.path, sheet_name='comments')
        for _, row in comments_table.iterrows():
            comment = Comment(row)
            comment.check_required_ids()
            self.comments.append(comment)

    def associate_comments_with_ideas(self):
        """
        Connects comments to ideas
        """
        for comment in self.comments:
            idea = self.ideas_dict.get(comment.idea_id)
            if idea:
                idea.add_comment(comment)
            else:
                raise ValueError(f"idea_id: {comment.idea_id} mentioned in comment {comment.comment_id} not found")

    def get_idea_by_id(self, idea_id):
        return self.ideas_dict.get(idea_id)

    def get_comment_by_id(self, comment_id):
        for comment in self.comments:
            if comment.comment_id == comment_id:
                return comment
        raise ValueError(f"Comment {comment_id} not found.")

    def sort_ideas_by_datetime(self):
        return sorted(self.ideas_dict.values(), key=lambda idea: idea.datetime)

    def sort_ideas_by_kudos(self):
        return sorted(self.ideas_dict.values(), key=lambda idea: idea.kudos, reverse=True)

    def get_ideas_info(self):
        """
        Get necessary information for displaying ideas.
        """
        return [
            {
                'name': idea.name,
                'introduction': idea.introduction,
                'name_1': idea.name_1,
                'kudos': idea.kudos
            }
            for idea in self.ideas_dict.values()
        ]

    def add_idea(self, name, introduction, name_1):
        """
        Adds a new idea to the dataset.
        """
        idea_id = max(self.ideas_dict.keys(), default=0) + 1
        idea_data = {
            'name': name,
            'introduction': introduction,
            'business_case': " ",
            'name_1': name_1,
            'department': " ",
            'kudos': 0,
            'stav': 'Nový',
            'datetime': pd.Timestamp(datetime.now()),
            'idea_id': idea_id,
            'comments': []
        }
        new_idea = Idea(pd.Series(idea_data))
        self.ideas_dict[idea_id] = new_idea
        print(f"Added new idea: {new_idea.name} with ID: {new_idea.idea_id}")
        return new_idea.idea_id


    def add_comment(self, idea_id, text):
        """
        Adds a new comment to an idea.
        """
        if idea_id not in self.ideas_dict:
            raise ValueError(f"Idea with ID {idea_id} does not exist.")

        comment_id = max([comment.comment_id for comment in self.comments], default=0) + 1
        comment_data = {
            'comment_id': comment_id,
            'idea_id': idea_id,
            'text': text,
            'kudos': 0,
            'datetime': pd.Timestamp(datetime.now())
        }
        new_comment = Comment(pd.Series(comment_data))
        self.comments.append(new_comment)
        self.ideas_dict[idea_id].add_comment(new_comment)


    def save_to_excel(self):
        """
        Save the Dataset back to the Excel file.
        """
        # Convert ideas to DataFrame
        ideas_data = [vars(idea) for idea in self.ideas_dict.values()]
        ideas_df = pd.DataFrame(ideas_data)

        # Convert comments to DataFrame
        comments_data = [vars(comment) for comment in self.comments]
        comments_df = pd.DataFrame(comments_data)

        # Write to Excel
        with pd.ExcelWriter(self.path) as writer:
            ideas_df.to_excel(writer, sheet_name='ideas', index=False)
            comments_df.to_excel(writer, sheet_name='comments', index=False)


class BaseEntry:
    """
    Template for comment or idea
    """

    def __init__(self, row: pd.Series):
        for column in row.index:
            setattr(self, column, row[column])

    def increase_kudos(self):
        self.kudos += 1

    def check_required_ids(self):
        raise NotImplementedError("Subclasses should implement this method")


class Idea(BaseEntry):
    """
    Represents a single idea in the dataset.
    """

    def __init__(self, row: pd.Series):
        super().__init__(row)
        self.comments = []

    def add_comment(self, comment):
        self.comments.append(comment)

    def get_comments(self):
        return self.comments

    def check_required_ids(self):
        if not hasattr(self, 'idea_id'):
            raise IndexError("Attempted to parse an idea, but column 'idea_id' not found")
        if not hasattr(self, 'datetime'):
            raise IndexError("Attempted to parse an idea, but column 'datetime' not found")
        if not hasattr(self, 'kudos'):
            raise IndexError("Attempted to parse an idea, but column 'kudos' not found")

    def update_or_create_attributes(self, attr_dict):
        """
        Update the values of an idea or create new attributes.
        """
        for attr, value in attr_dict.items():
            setattr(self, attr, value)


class Comment(BaseEntry):
    """
    Represents a single comment in the dataset.
    """

    def check_required_ids(self):
        if not hasattr(self, 'idea_id'):
            raise IndexError("Attempted to parse a comment, but column 'idea_id' not found")
        if not hasattr(self, 'comment_id'):
            raise IndexError("Attempted to parse a comment, but column 'comment_id' not found")
