
import trueskill
skill_env = trueskill.TrueSkill(draw_probability=0.0)
skill_env.make_as_global() # just in case we goof

__rating = skill_env.Rating()
default_mu = __rating.mu
default_sigma = __rating.sigma
default_exposure = skill_env.expose(__rating)
