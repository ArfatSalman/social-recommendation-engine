
from .models import graph

def create_uniqueness_constraint(label, property):
	query = "CREATE CONSTRAINT ON (n:{label}) ASSERT n.{property} IS UNIQUE"
	query.format(label=label, property=property)
	graph.cypher.exceute(query)

#create_uniqueness_constraint('User', 'email')
