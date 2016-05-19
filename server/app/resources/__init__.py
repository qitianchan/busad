# -*- coding: utf-8 -*-
from flask_restful import Api
from .user import UserAPI, UserList, AuthToken
from .district import DistrictAPI, District_Resource
from .route_resources import RouteAPI, RouteList
from .bus_resources import BusList, BusAPI
from .login import Login
from .publish_ad import Publish
from .progress import Progress
from .user_info import UserInfo
from .abort import AbortPublish
from .group_resources import GroupList, GroupAPI, GroupMember
# flask_restful
api = Api(prefix='/api')

api.add_resource(UserAPI, '/users/<int:id>')
api.add_resource(UserList, '/users')

api.add_resource(AuthToken, '/token')

api.add_resource(District_Resource, '/districts')
api.add_resource(DistrictAPI, '/districts/<int:id>')

api.add_resource(RouteList, '/routes')
api.add_resource(RouteAPI, '/routes/<int:id>')

api.add_resource(BusList, '/buses')
api.add_resource(BusAPI, '/buses/<int:id>')

api.add_resource(Login, '/login')

api.add_resource(Publish, '/publish')
api.add_resource(Progress, '/progress/<string:progress_code>')

api.add_resource(UserInfo, '/userinfo/<string:nothing_to_do>')

api.add_resource(AbortPublish, '/abort/<string:progress_code>')

api.add_resource(GroupList, '/group')
api.add_resource(GroupAPI, '/group/<int:id>')
api.add_resource(GroupMember, '/group/<int:group_id>/members')
