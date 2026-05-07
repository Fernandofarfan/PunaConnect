from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from typing import List, Optional

Base = declarative_base()

class Team(Base):
    __tablename__ = 'teams'
    id = Column(Integer, primary_key=True, autoincrement=True)
    members = relationship("User", back_populates="team")

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True) # Telegram User ID
    username = Column(String, nullable=True)
    fullname = Column(String, nullable=False)
    role = Column(String, nullable=False)
    modality = Column(String, nullable=False)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=True)
    
    team = relationship("Team", back_populates="members")

import os

DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///hackathon.db')
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

def register_user(user_id: int, username: str, fullname: str, role: str, modality: str):
    with SessionLocal() as session:
        user = session.query(User).filter(User.id == user_id).first()
        if user:
            user.username = username
            user.fullname = fullname
            user.role = role
            user.modality = modality
        else:
            user = User(id=user_id, username=username, fullname=fullname, role=role, modality=modality)
            session.add(user)
        session.commit()

def get_user(user_id: int) -> Optional[User]:
    with SessionLocal() as session:
        return session.query(User).filter(User.id == user_id).first()

def get_team_members(team_id: int) -> List[User]:
    with SessionLocal() as session:
        return session.query(User).filter(User.team_id == team_id).all()

def match_user(user_id: int) -> Optional[Team]:
    with SessionLocal() as session:
        user = session.query(User).filter(User.id == user_id).first()
        if not user or user.team_id:
            return None
            
        unmatched_users = session.query(User).filter(User.team_id == None, User.id != user_id).all()
        
        team_members = [user]
        selected_roles = {user.role}
        
        remaining_users = []
        for u in unmatched_users:
            if u.role not in selected_roles and len(team_members) < 4:
                team_members.append(u)
                selected_roles.add(u.role)
            else:
                remaining_users.append(u)
                
        for u in remaining_users:
            if len(team_members) < 4:
                team_members.append(u)
            else:
                break
                
        if len(team_members) > 1:
            new_team = Team()
            session.add(new_team)
            session.commit() 
            
            for member in team_members:
                member.team_id = new_team.id
                session.add(member)
            
            session.commit()
            return new_team
            
        return None
